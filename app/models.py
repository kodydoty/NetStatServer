
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    zipcode = Column(String)
    api_key = Column(String, unique=True)
    items = relationship('SpeedTest', back_populates='owner')

class SpeedTest(Base):
    __tablename__ = 'speedtests'
    id = Column(Integer, primary_key=True, index=True)
    isp = Column(String, index=True)
    zipcode = Column(String, index=True)
    download = Column(Integer)
    upload = Column(Integer)
    ping = Column(Integer)
    api_key = Column(String, ForeignKey('users.api_key'))
    owner = relationship('User', back_populates='items')
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    temperature = Column(Integer, nullable=True)
    condition = Column(String, nullable=True)
