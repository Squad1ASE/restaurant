import connexion
from database import db_session, Restaurant, Table 
from flask import request, jsonify, abort, make_response
import json


def create_restaurant():
    request_dict = request.json

    new_tables = []
    tot_capacity = 0
    tables = request_dict.pop('tables')
    for table in tables:
        new_table = Table(**table)
        tot_capacity += new_table.capacity
        new_tables.append(new_table)

    new_restaurant = Restaurant(**request_dict)
    new_restaurant.capacity = tot_capacity
    new_restaurant.tables = new_tables

    db_session.add(new_restaurant)
    db_session.commit()

    return 'Restaurant successfully created'


def get_restaurants():  
    q = db_session.query(Restaurant).all()
    return [p.serialize() for p in q]


def get_restaurant(restaurant_id):
    q = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if q is not None:
        return q.serialize()
    else:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")


def edit_restaurant(restaurant_id):
    request_dict = request.json
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if restaurant is None:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")

    tables = request_dict.pop('tables', None)
    if tables is not None:
        new_tables = []
        tot_capacity = 0
        for table in tables:
            new_table = Table(**table)
            tot_capacity += new_table.capacity
            new_tables.append(new_table)
        
        restaurant.capacity = tot_capacity
        restaurant.tables = new_tables

    new_phone = request_dict.pop('phone', None)
    if new_phone is not None:
        restaurant.phone = new_phone

    db_session.commit()

    return 'Restaurant successfully edited'