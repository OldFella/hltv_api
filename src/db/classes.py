from sqlalchemy import Column, Integer, String, Date, Float
from .base_class import Base

class sides(Base):
    __tablename__ = 'sides'
    sideid = Column(Integer, primary_key = True)
    name = Column(String)

class teams(Base):
    __tablename__ = 'teams'
    teamid = Column(Integer, primary_key = True)
    name = Column(String)

class players(Base):
    __tablename__ = 'players'
    playerid = Column(Integer, primary_key=True)
    name = Column(String)

class maps(Base):
    __tablename__ = 'maps'
    mapid = Column(Integer, primary_key=True)
    name = Column(String)

class match_overview(Base):
    __tablename__ = 'match_overview'
    matchid = Column(Integer, primary_key = True)
    event = Column(String)
    date = Column(Date)

class matches(Base):
    __tablename__ = 'matches'
    matchid = Column(Integer, primary_key = True)
    teamid = Column(Integer, primary_key = True)
    mapid = Column(Integer, primary_key = True)
    sideid = Column(Integer, primary_key = True)
    score = Column(Integer)

class player_stats(Base):
    matchid= Column(Integer, primary_key = True)
    playerid= Column(Integer, primary_key = True)
    teamid= Column(Integer, primary_key = True)
    mapid= Column(Integer, primary_key = True)
    sideid= Column(Integer, primary_key = True)
    k = Column(Integer)
    d = Column(Integer)
    ek = Column(Integer)
    ed = Column(Integer)
    roundswing = Column(Float)
    adr = Column(Float)
    eadr = Column(Float)
    kast = Column(Float)
    ekast = Column(Float)
    rating = Column(Float)

class fantasy_overview(Base):
    fantasyid= Column(Integer, primary_key = True)
    name = Column(String)

class fantasies(Base):
    fantasyid= Column(Integer, primary_key = True)
    teamid= Column(Integer, primary_key = True)
    playerid = Column(Integer, primary_key = True)
    cost = Column(Integer)

