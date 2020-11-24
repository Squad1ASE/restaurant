import os
from sqlalchemy import create_engine, Column, Integer, Float, Text, Unicode, ForeignKey, PickleType, Boolean, Date
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from static.enum import CUISINE_TYPES, WEEK_DAYS
import time
import datetime
import inspect


#DATABASEURI = os.environ['DATABASE_URI']
db = declarative_base()
#engine = create_engine(DATABASEURI, convert_unicode=True)
engine = create_engine('sqlite:///restaurant.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    try:
        db.metadata.create_all(bind=engine)
        q = db_session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        '''
        if restaurant is None:
            example = Restaurant()
            example.name = 'Trial Restaurant'
            example.likes = 42
            example.phone = 555123456
            example.lat = 43.720586
            example.lon = 10.408347
            db_session.add(example)
            db_session.commit()
        '''
    except Exception as e:
        print(e)


class Restaurant(db):
    __tablename__ = 'restaurant'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    owner_id = Column(Integer, CheckConstraint('owner_id > 0'), nullable=False)

    name = Column(Unicode(128), CheckConstraint('length(name) > 0'), nullable=False)
    lat = Column(Float, nullable=False) 
    lon = Column(Float, nullable=False) 
    phone = Column(Unicode(128), CheckConstraint('length(phone) > 0'), nullable=False)

    capacity = Column(Integer, CheckConstraint('capacity > 0'), nullable=False)
    prec_measures = Column(Unicode(128), nullable=False)

    cuisine_type = Column(PickleType, CheckConstraint('length(cuisine_type) > 0'), nullable=False)

    # average time to eat, expressed in minutes 
    avg_time_of_stay = Column(Integer, CheckConstraint('avg_time_of_stay >= 15'), nullable=False)

    tot_reviews = Column(Integer, CheckConstraint('tot_reviews >= 0'), default=0)   # periodically updated in background
    avg_rating = Column(Float, CheckConstraint('avg_rating >= 0 and avg_rating <= 5'), default=0)
    likes = Column(Integer, CheckConstraint('likes >= 0'), default=0)    # periodically updated in background

    tables = relationship("Table", cascade="all,delete,delete-orphan", backref="restaurant")
    working_days = relationship("WorkingDay", cascade="all,delete,delete-orphan", backref="restaurant")
    dishes = relationship("Dish", cascade="all,delete,delete-orphan", backref="restaurant")

    @validates('owner_id', 'capacity')
    def validate_positive_integer(self, key, value):
        return _validate_integer(key, value)

    @validates('name', 'phone')
    def validate_string_not_empty(self, key, value):
        return _validate_string(key, value)

    @validates('prec_measures')
    def validate_prec_measures(self, key, value):
        return _validate_string(key, value, None)

    @validates('lat', 'lon')
    def validate_position(self, key, value):
        return _validate_float(key, value, None)

    @validates('cuisine_type')
    def validate_cuisine_type(self, key, cuisine_types):
        if not isinstance(cuisine_types, list): raise ValueError("cuisine_type is not a list")
        if any(i not in CUISINE_TYPES for i in cuisine_types): raise ValueError("cuisine_type elements are not strings")
        if (len(cuisine_types) == 0): raise ValueError("cuisine_type is empty")
        return cuisine_types

    @validates('avg_time_of_stay')
    def validate_avg_time_of_stay(self, key, value):
        return _validate_integer(key, value, 14)

    @validates('tot_reviews', 'likes')
    def validate_positive_integer_or_zero(self, key, value):
        return _validate_integer(key, value, -1)

    @validates('avg_rating')
    def validate_avg_rating(self, key, value):
        return _validate_float(key, value, 0, 5)

    def serialize(self):
        complex_fields = ['tables', 'working_days']
        serialized = dict([(k,v) for k,v in self.__dict__.items() if k not in complex_fields and k[0] != '_' and not inspect.ismethod(v)])
        tables, working_days, dishes = [], [], []
        for table in self.tables:
            tables.append(table.serialize())
        serialized['tables'] = tables
        for wd in self.working_days:
            working_days.append(wd.serialize())
        serialized['working_days'] = working_days
        for dish in self.dishes:
            dishes.append(dish.serialize())
        serialized['dishes'] = dishes
        return serialized


class Table(db):
    __tablename__ = 'table'

    id = Column(Integer, primary_key=True, autoincrement=True)

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)

    name = Column(Unicode(128), CheckConstraint('length(name) > 0'), nullable=False)   
    capacity = Column(Integer, CheckConstraint('capacity > 0'), nullable=False)

    @validates('restaurant_id', 'capacity')
    def validate_integer(self, key, value):
        return _validate_integer(key, value)

    @validates('name')
    def validate_name(self, key, value):
        return _validate_string(key, value)

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])


class WorkingDay(db):
    __tablename__ = 'working_day'

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False, primary_key=True)

    day = Column(Unicode(128), nullable=False, primary_key=True)
    work_shifts = Column(PickleType, nullable=False)  

    @validates('restaurant_id')
    def validate_restaurant_id(self, key, value):
        return _validate_integer(key, value)
        
    @validates('day')
    def validate_day(self, key, day):
        if day is None: raise ValueError("day is None")
        if day not in WEEK_DAYS: raise ValueError("day is not a week day")
        return day

    @validates('work_shifts')
    def validate_work_shifts(self, key, work_shifts):
        if (work_shifts is None): raise ValueError("work_shifts is None")
        if not isinstance(work_shifts, list): raise ValueError("work_shifts is not a list")
        if (len(work_shifts) == 0): raise ValueError("work_shifts is empty")
        if (len(work_shifts) > 2): raise ValueError("work_shifts can contains at most two shifts")
        last = None
        for shift in work_shifts:
            if not isinstance(shift, list): raise ValueError("work_shift element is not a list")
            if (len(shift) != 2): raise ValueError("work_shift element is not a pair")
            for hour_to_check in shift:
                try:
                    hour = time.strptime(hour_to_check, '%H:%M')
                except:
                    raise ValueError("incorrect format for hour")
                if last is None:
                    last = hour
                else:
                    if last >= hour:
                        raise ValueError("the hours provided must be in ascending order")
                    last = hour     
        return work_shifts

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])


class Dish(db):
    __tablename__ = 'dishes'
    id = Column(Integer, primary_key=True, autoincrement=True)

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)

    name = Column(Unicode(128), CheckConstraint('length(name) > 0'), nullable=False)
    price = Column(Float, CheckConstraint('price>0'), nullable=False)
    ingredients = Column(Unicode(128), CheckConstraint('length(ingredients) > 0'), nullable=False)

    @validates('restaurant_id')
    def validate_restaurant_id(self, key, value):
        return _validate_integer(key, value)

    @validates('name', 'ingredients')
    def validate_string(self, key, value):
        return _validate_string(key, value)

    @validates('price')
    def validate_price(self, key, value):
        return _validate_float(key, value, 0.001)

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])


class Like(db):
    __tablename__ = 'like'

    user_id = Column(Integer, primary_key=True)

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), primary_key=True)
    restaurant = relationship('Restaurant', foreign_keys='Like.restaurant_id')

    marked = Column(Boolean, default=False) 

    @validates('user_id','restaurant_id')
    def validate_integer(self, key, value):
        return _validate_integer(key, value)

    @validates('marked')
    def validate_marked(self, key, value):
        return _validate_boolean(key, value)

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])


class Review(db):
    __tablename__ = 'review'

    user_id = Column(Integer, primary_key=True)

    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), primary_key=True)
    restaurant = relationship('Restaurant', foreign_keys='Review.restaurant_id')

    marked = Column(Boolean, default=False)
    rating = Column(Integer, CheckConstraint('rating >= 0 and rating <= 5'), nullable=False)
    comment = Column(Unicode(128), CheckConstraint('length(comment) > 0'), nullable=False)
    date = Column(Date, nullable=False)

    @validates('user_id','restaurant_id')
    def validate_integer(self, key, value):
        return _validate_integer(key, value)

    @validates('marked')
    def validate_marked(self, key, value):
        return _validate_boolean(key, value)

    @validates('rating')
    def validate_rating(self, key, value):
        if value is None: raise ValueError(str(key) + " is None")
        if not isinstance(value, int): raise ValueError(str(key) + " is not an int")
        if value < 1 or value > 5: 
            raise ValueError(str(key) + " must be must be between 1 and 5 (inclusive)")
        return value

    @validates('comment')
    def validate_comment(self, key, value):
        return _validate_string(key, value)

    @validates('date')
    def validate_date(self, key, value):
        if value is None: raise ValueError(str(key) + " is None")
        if not isinstance(value, datetime.datetime): raise ValueError(str(key) + " is not a datetime")
        return value

    def serialize(self):
        serialized = dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_' and k not in ['date','marked']])
        serialized['date'] = self.date.strftime("%d/%m/%Y")
        return serialized


# Table to track deleted databases.
# The information contained in it will allow the celery tasks to complete
# the cancellation by asynchronously deleting Likes, Reviews and Reservations
class RestaurantDeleted(db):
    __tablename__ = 'restaurant_deleted'

    id = Column(Integer, primary_key=True)

    name = Column(Unicode(128), CheckConstraint('length(name) > 0'), nullable=False)

    likes_deleted = Column(Boolean, default=False)
    reviews_deleted = Column(Boolean, default=False)
    reservations_service_notified = Column(Boolean, default=False)
        
    @validates('id')
    def validate_id(self, key, value):
        return _validate_integer(key, value)

    @validates('name')
    def validate_name(self, key, value):
        return _validate_string(key, value)
    
    @validates('likes_deleted', 'reviews_deleted', 'reservations_service_notified')
    def validate_boolean(self, key, value):
        return _validate_boolean(key, value)

    def serialize(self):
        return dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])


# private validators
def _validate_boolean(key, value):
    if value is None: raise ValueError(str(key) + " is None")
    if not isinstance(value, bool): raise ValueError(str(key) + " is not a boolean")
    return value

def _validate_integer(key, value, greater_than=0):
    if value is None: raise ValueError(str(key) + " is None")
    if not isinstance(value, int): raise ValueError(str(key) + " is not an integer")
    if value <= greater_than: raise ValueError(str(key) + " must be greater than " + str(greater_than))
    return value

def _validate_float(key, value, min_value=0, max_value=None):
    if value is None: raise ValueError(str(key) + " is None")
    if not isinstance(value, float) and not isinstance(value, int): raise ValueError(str(key) + " is not a float or int")
    if min_value is not None and value < min_value: 
        raise ValueError(str(key) + " must be greater or equal than " + str(min_value))
    if max_value is not None and value > max_value: 
        raise ValueError(str(key) + " must be less or equal than " + str(max_value))
    return value

def _validate_string(key, value, greater_than=0):
    if value is None: raise ValueError(str(key) + " is None")
    if not isinstance(value, str): raise ValueError(str(key) + " is not a string")
    if greater_than is not None:
        if len(value) <= greater_than: raise ValueError(str(key) + " must be greater than " + str(greater_than))
    return value