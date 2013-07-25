from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session

from datetime import datetime
from bs4 import BeautifulSoup

import os
import requests
import json
import re

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

    def process_query_for_all_captures(self, query_function):
        for c in self.captures:
            query_function(c)
        session.commit()


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    captured_on = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("captures", order_by=captured_on, cascade="all, delete-orphan"))
    queries = relationship("Query", cascade="all, delete-orphan")

    def get_soup_for_capture(self):
        soup = BeautifulSoup(self.raw_text)
        return soup

    def process_query(self, query_name, query_function):
        #  TODO run query, and create new query object with name/result
        pass

    def make_query_for_page_length(self):
        page_length = len(self.raw_text)
        q = Query(capture_id=self.id, site_id=self.site_id, query="page_length", result=page_length)
        session.add(q)

    def make_query_for_num_images(self):
        soup = BeautifulSoup(self.raw_text, "lxml")
        img_list = soup("img")
        q = Query(capture_id=self.id, query="num_images", result=len(img_list))
        session.add(q)


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    capture_id = Column(Integer, ForeignKey('captures.id'))
    site_id = Column(Integer, ForeignKey('sites.id'))
    query = Column(String)
    result = Column(Integer)



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
