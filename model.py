from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session

from datetime import datetime
import time
from bs4 import BeautifulSoup
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
            query.calculate_query(c)

    def get_data_for_display(self, query_name):
        key = str(self.id) + ":" + query_name
        data = rdb.hgetall(key)
        dates = sorted(map(int, data.keys()))
        json_data = []
        for coord in dates:
            json_data.append({'x': int(coord), 'y': int(data[str(coord)])})
        return json_data


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    captured_on = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("captures", order_by=captured_on, cascade="all, delete-orphan"))

    def process_all_queries(self):
        soup = BeautifulSoup(self.raw_text, "lxml")
        queries = session.query(Query).all()
        for q in queries:
            q.calculate_query(self, soup)


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)       # short variableized vesion of name, used for getting calc function
    long_name = Column(String)  # print-friendly version of query name
    aggr_format = Column(String) # TODO: should this be something else? enum?
    type = Column(String)
    tag_name = Column(String)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'query'
    }

    def run_query_on_all_sites(self):
        captures = session.query(Capture).all()
        for c in captures:
            self.calculate_query(c)
        session.commit()
        # run aggregate calculation after adding new site data
        self.aggregate_for_all_sites()

    # takes the y value passed in and adds x,y coordinate to redis for that capture's hash
    def calculate_query(self, capture, y):
        key = str(capture.site_id) + ":" + self.name
        x = int(time.mktime(capture.captured_on.timetuple()))
        rdb.hset(key, x, y)

    #  wipes existing aggregate data, and recalculates. default is to calculate the avg
    def aggregate_for_all_sites(self):
        self.reset_aggregate()
        keys = rdb.keys('*:'+self.name)
        data = map(self.map_to_date_result_pair, keys)  # list of dicts for each site w/ quarter/value pairs
        aggr_result = self.group_by_quarter(data)  # dict with quarter/aggregated value pairs
        for quarter in aggr_result.iterkeys():
            rdb.hset("all:"+self.name, quarter, aggr_result[quarter])

    def map_to_date_result_pair(self, site):
        data = rdb.hgetall(site).items()  # list of timestamp/value tuples (832848234, 5)
        data = {self.get_quarter_and_year(item[0]): float(item[1]) for item in data}  # dict of quarter/value pairs
        return data

    # takes in list of dicts of quarter/value pairs, returns dict w/ aggregated value
    def group_by_quarter(self, data):
        temp = {}
        result = {}
        for site in data:
            for quarter in site.iterkeys():
                if temp.get(quarter):
                    temp[quarter].append(site[quarter])
                else:
                    temp[quarter] = [site[quarter]]
        for quarter in temp.iterkeys():
            result[quarter] = self.calculate_aggr(temp[quarter])
        return result


    def get_aggregate_data(self):
        result = []
        key = 'all:' + self.name
        data = rdb.hgetall(key).items()
        for coord in data:
            year, quarter = coord[0].split(":")
            month = (int(quarter) % 4)*3 + 1
            x = int(time.mktime(datetime(int(year), month, 1).timetuple()))
            result.append({'x':x, 'y':float(coord[1])})
        return sorted(result, key=lambda coord: coord['x'])

    def get_quarter_and_year(self, date_str):
        date = datetime.fromtimestamp(float(date_str))
        quarter = (date.month-1)/3 + 1
        return str(date.year) + ":" + str(quarter)

    def date_from_quarter_int(self, x):
        year = 1996+(x/4)
        month = 1+(x%4)*3
        return int(time.mktime(datetime(year, month, 1).timetuple()))

    #  deletes all aggregate data for this query
    def reset_aggregate(self):
        key = "all:" + self.name
        rdb.delete(key)


class CountTagQuery(Query):
    __mapper_args__ = {
        'polymorphic_identity': 'count_tag'
    }

    def calculate_query(self, capture, soup=None):
        if not soup:
            soup = BeautifulSoup(capture.raw_text, "lxml")
        tag_list = soup(self.tag_name)
        result = len(tag_list)
        super(CountTagQuery, self).calculate_query(capture, result)

    # takes in list of values and returns aggregated value
    def calculate_aggr(self, data):
        return sum(data)/len(data)

class HasTagQuery(Query):
    __mapper_args__ = {
        'polymorphic_identity': 'has_tag'
    }

    def calculate_query(self, capture, soup=None):
        if not soup:
            soup = BeautifulSoup(capture.raw_text, "lxml")
        tag_list = soup.find(self.tag_name)
        if tag_list:
            result = 1
        else:
            result = 0
        super(HasTagQuery, self).calculate_query(capture, result)

    def calculate_aggr(self, data):
        return 100 * sum(data) / len(data)


class LengthQuery(Query):
    __mapper_args__ = {
        'polymorphic_identity': 'length'
    }
    def calculate_query(self, capture, soup):
        result = len(capture.raw_text)
        super(LengthQuery, self).calculate_query(capture, result)

    def calculate_aggr(self, data):
        return sum(data)/len(data)

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
