import os
from sqlalchemy import create_engine, Column, Integer, Float, Text, Unicode
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASEURI = os.environ['DATABASE_URI']
db = declarative_base()
engine = create_engine(DATABASEURI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                             bind=engine))


def init_db():
    try:
        db.metadata.create_all(bind=engine)
        q = db_session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            example = Restaurant()
            example.name = 'Trial Restaurant'
            example.likes = 42
            example.phone = 555123456
            example.lat = 43.720586
            example.lon = 10.408347
            db_session.add(example)
            db_session.commit()
    except Exception as e:
        print(e)


class Restaurant(db):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128)) 
    likes = Column(Integer) # will store the number of likes, periodically updated in background
    lat = Column(Float) # restaurant latitude
    lon = Column(Float) # restaurant longitude
    phone = Column(Unicode(128))

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])
