from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session

from datetime import datetime
import time
from bs4 import BeautifulSoup
import json

import redis

rdb = redis.StrictRedis(host="localhost", port=6379, db=0)

engine = create_engine("postgresql://localhost/webhistory")
session = scoped_session(sessionmaker(bind=engine,
                                    autocommit=False,
                                    autoflush=False))
Base = declarative_base()
Base.query = session.query_property()

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)

    def add_capture(self, timestamp, raw_text):
        dt = datetime(year=int(timestamp[0:4]), month=int(timestamp[4:6]),
                    day=int(timestamp[6:8]), hour=int(timestamp[8:10]),
                    minute=int(timestamp[10:12]), second=int(timestamp[12:14]))
        c = Capture(site_id=self.id, captured_on=dt, raw_text=raw_text)
        session.add(c)
        session.commit()

    def clear_all_captures(self):
        map(session.delete, self.captures)
        session.commit()

    def process_query_for_all_captures(self, query):
        for c in self.captures:
            key = str(self.id) + ":" + query.name
            x = time.mktime(c.captured_on.timetuple())
            y = query.calculate_query(c)
            #rdb.zadd(key, x, y)

    def get_data_for_display(self, query_name):
        key = str(self.id) + ":" + query_name
        data = rdb.hgetall(key)
        dates = sorted(map(int, data.keys()))
        json_data = []
        for coord in dates:
            json_data.append({'x': int(coord), 'y': int(data[str(coord)]) })
        # TODO: make this return less hacky (is there a way?)
        return json_data  # return with quote marks removed



class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    captured_on = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("captures", order_by=captured_on, cascade="all, delete-orphan"))

    def process_all_queries(self):
        soup = BeautifulSoup(capture.raw_text, "lxml")
        queries = session.query(Query).all()
        for q in queries:
            q.calculate_query(self, soup)

    # def get_soup_for_capture(self):
    #     soup = BeautifulSoup(self.raw_text)
    #     return soup


# TODO: make sure i dont need the below 2 functions anymore.
    # def process_one_query(self, query_name):
    #     key = str(self.id) + ":" + query.name
    #     x = time.mktime(c.captured_on.timetuple())
    #     y = query.calculate_query(c)









class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)       # short variableized vesion of name, used for getting calc function
    long_name = Column(String)  # print-friendly version of query name
    aggr_format = Column(String) # TODO: should this be something else? enum?

    def run_query_on_all_sites(self):
        captures = session.query(Capture).all()
        for c in captures:
            self.calculate_query(c)
        session.commit()
        # run aggregate calculation after adding new site data
        self.aggregate_for_all_sites()

    # runs the correct calculate function for this query for the given capture
    def calculate_query(self, capture, soup):
        calc_function = getattr(self, "calculate_%s" % self.name)
        key = str(capture.site_id) + ":" + self.name
        if not soup:
            soup = BeautifulSoup(capture.raw_text, "lxml")
        x = int(time.mktime(capture.captured_on.timetuple()))
        y = calc_function(capture, soup)  # TODO: should probably change calc_function to not need capture
        rdb.hset(key, x, y)
        return y

    #  ---- CALCULATE FUNCTIONS -----
    def calculate_page_length(self, capture):
        page_length = len(capture.raw_text)
        return page_length

    def calculate_num_images(self, capture, soup):
        img_list = soup("img")
        return len(img_list)

    def calculate_num_maps(self, capture, soup):
        num_maps = len(soup("map"))
        return num_maps

    #  ----- END CALCULATE FUNCTIONS -----

    #  will wipe any aggregate data currently stored for query (if any), and reaggregate
    def aggregate_for_all_sites(self):
        self.reset_aggregate()
        keys = rdb.keys('*:'+self.name)
        for k in keys:  # go through all sites
            # go through all captures (aka coordinates)
            # use hincrby to add each coordinate to the correct aggretate hash
            coords = rdb.hgetall(k)
            for timestamp in coords.iterkeys():
                value = int(coords[timestamp])
                quarter, year = self.get_quarter_and_year(int(timestamp))
                aggr_key = "all:" + self.name + ":" + str(year)
                rdb.hincrby(aggr_key, str(quarter)+"_sum", value)
                if value > 0:
                    rdb.hincrby(aggr_key, str(quarter)+"_has_one")
                rdb.hincrby(aggr_key, str(quarter)+"_count")

    #  returns the aggregated data
    #  method parameter specifies how to aggregate (avg, percent_contains, etc.)
    #  TODO: should i be using map? reduce?
    def get_aggregate_data(self, method="avg"):
        if self.aggr_format == "Percent of Sites that Contain":
            method = "percent_contains"
        json_data = []
        keys = rdb.keys('all:'+self.name+":*")
        x = 0
        for year in range(1996,2014): #  TODO probably shouldn't hardcode these years...globals?
            k = 'all:' + self.name + ":" + str(year)
            for q in "1234":
                q_count = rdb.hget(k, q+"_count")
                if q_count:  # only add a data point if there is a count
                    if method == "avg":
                        q_sum = rdb.hget(k, q+"_sum")
                        avg = int(q_sum)/float(q_count)
                        json_data.append({'x':x, 'y':avg})
                    elif method == "percent_contains":
                        q_has_one = rdb.hget(k, q+"_has_one")
                        if not q_has_one:
                            q_has_one = 0
                        percent = 100 * int(q_has_one)/float(q_count)
                        json_data.append({'x':x, 'y':percent})
                x += 1
        return json_data


    def get_quarter_and_year(self, date):
        date = datetime.fromtimestamp(date)
        quarter = (date.month-1)/3 + 1
        return (quarter, date.year)

    #  will reset aggregate data for this query
    def reset_aggregate(self):
        key_base = "all:" + self.name + ":*"
        for key in rdb.keys(pattern=key_base):
            rdb.delete(key)
            # TODO needs to be finished


#  Given a url, either add it to the sites table, or update it if it already exists
def add_or_refresh_site(url):
    url = clean_url(url)
    site = session.query(Site).filter_by(url=url).first()
    #  if there's already entry for that site, remove all captures
    if site:
        site.clear_all_captures()
    #  add to sites table
    else:
        site = Site(url=url)
        session.add(site)
    session.commit()
    return site

#  strips off trailing slash if its there
def clean_url(url):
    return url.rstrip("/")
