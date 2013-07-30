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

    def process_query_for_all_captures(self, query_name):
        query = session.query(Query).filter_by(name=query_name).one()
        for c in self.captures:
            key = str(self.id) + ":" + query_name
            x = time.mktime(c.captured_on.timetuple())
            value = "{x: %d, y: %d }" % (x, query.calculate_query(c))
            rdb.zadd(key, x, value)

    def get_data_for_display(self, query_name):
        key = str(self.id) + ":" + query_name
        data = rdb.zrange(key, 0, -1)
        return json.dumps(data).translate(None, '"')  # return with quote marks removed



class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    captured_on = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("captures", order_by=captured_on, cascade="all, delete-orphan"))

    # def get_soup_for_capture(self):
    #     soup = BeautifulSoup(self.raw_text)
    #     return soup

    def process_one_query(self, query_name):
        #  TODO add to redis
        query = session.query(Query).filter_by(name=query_name).one()
        return query.calculate_query(self)

    def process_all_queries(self):
        queries = session.query(Query).all()
        for q in queries:
            q.calculate_query(self)







class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)       # short variableized vesion of name, used for getting calc function
    long_name = Column(String)  # print-friendly version of query name

    # runs the correct calculate function for this query for the given capture
    def calculate_query(self, capture):
        calc_function = getattr(self, "calculate_%s" % self.name)
        return calc_function(capture)

    def calculate_page_length(self, capture):
        page_length = len(capture.raw_text)
        #TODO need to add to redis
        return page_length

    def calculate_num_images(self, capture):
        soup = BeautifulSoup(capture.raw_text, "lxml")
        img_list = soup("img")
        #TODO need to add to redis
        return len(img_list)

    def calculate_num_maps(self, capture):
        soup = BeautifulSoup(capture.raw_text, "lxml")
        num_maps = len(soup("map"))
        #TODO need to add to redis
        return num_maps

    #  will wipe any aggregate data currently stored for query (if any), and reaggregate 
    def aggregate_for_all_sites(self):
        keys = rdb.keys ('*:'+self.name) 
        for k in keys:  # go through all sites
            

    #  will create (or reinitialize) aggregate data for this query
    def initialize_aggregate(self):
        key_base = "all:" + self.name + ":"
        for year in range(1996, 2014):

            key = key_base + str(i)
            rdb.hmset(key, )





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
