from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session

engine = create_engine("postgresql://localhost/webhistory", echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                    autocommit=False,
                                    autoflush=False))
Base = declarative_base()
Base.query = session.query_property()

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    num_captures = Column(Integer, default=0)


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'))
    timestamp = Column(DateTime)
    raw_text = Column(Text)

    site = relationship("Site", backref=backref("sites", order_by=timestamp))


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    capture_id = Column(Integer, ForeignKey('captures.id'))
    query = Column(String)
    result = Column(Integer)

