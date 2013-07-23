from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session

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
        c = Capture(site_id=self.id, timestamp=timestamp, raw_text=raw_text)
        session.add(c)
        session.commit()

    def clear_all_captures(self):
        map(session.delete, self.captures)
        session.commit()


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    timestamp = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("captures", order_by=timestamp, cascade="all, delete-orphan"))
    queries = relationship("Query", cascade="all, delete-orphan")


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    capture_id = Column(Integer, ForeignKey('captures.id'))
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
