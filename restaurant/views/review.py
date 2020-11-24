import connexion
from database import db_session, Restaurant, Table, WorkingDay, Dish, RestaurantDeleted
from flask import request
from sqlalchemy import or_, and_
import json


def create_review():
    request_dict = request.json

    # tables
    new_tables = []
    tot_capacity = 0
    tables = request_dict.pop('tables')
    for table in tables:
        new_table = Table()
        new_table.name = table['name'] 
        new_table.capacity = table['capacity']
        tot_capacity += new_table.capacity
        new_tables.append(new_table)

    # working days
    new_wds, days_already_present = [], []
    working_days = request_dict.pop('working_days')
    for wd in working_days:
        if wd['day'] in days_already_present:
            return connexion.problem(400, "Bad Request", "There are two working days with the same day of the week")
        try:
            new_wd = WorkingDay(**wd)
            new_wd.day = wd['day'] 
            new_wd.work_shifts = wd['work_shifts']
            new_wds.append(new_wd)
        except ValueError as e:
            return connexion.problem(400, "Bad Request", str(e))
        days_already_present.append(wd['day'])

    # dishes
    new_dishes = []
    dishes = request_dict.pop('dishes')
    for dish in dishes:
        new_dish = Dish()
        new_dish.name = dish['name'] 
        new_dish.price = dish['price'] 
        new_dish.ingredients = dish['ingredients'] 
        new_dishes.append(new_dish)

    # restaurant
    expected_keys = ['owner_id', 'name', 'lat', 'lon', 'phone', 'prec_measures', 'cuisine_type', 'avg_time_of_stay']
    request_dict = dict((k, request_dict[k]) for k in request_dict.keys() if k in expected_keys)
    new_restaurant = Restaurant(**request_dict)
    new_restaurant.capacity = tot_capacity
    new_restaurant.tables = new_tables
    new_restaurant.working_days = new_wds
    new_restaurant.dishes = new_dishes

    db_session.add(new_restaurant)
    db_session.commit()

    return 'Restaurant successfully created'


def get_reviews():
    request_dict = request.json

    # tables
    new_tables = []
    tot_capacity = 0
    tables = request_dict.pop('tables')
    for table in tables:
        new_table = Table()
        new_table.name = table['name'] 
        new_table.capacity = table['capacity']
        tot_capacity += new_table.capacity
        new_tables.append(new_table)

    # working days
    new_wds, days_already_present = [], []
    working_days = request_dict.pop('working_days')
    for wd in working_days:
        if wd['day'] in days_already_present:
            return connexion.problem(400, "Bad Request", "There are two working days with the same day of the week")
        try:
            new_wd = WorkingDay(**wd)
            new_wd.day = wd['day'] 
            new_wd.work_shifts = wd['work_shifts']
            new_wds.append(new_wd)
        except ValueError as e:
            return connexion.problem(400, "Bad Request", str(e))
        days_already_present.append(wd['day'])

    # dishes
    new_dishes = []
    dishes = request_dict.pop('dishes')
    for dish in dishes:
        new_dish = Dish()
        new_dish.name = dish['name'] 
        new_dish.price = dish['price'] 
        new_dish.ingredients = dish['ingredients'] 
        new_dishes.append(new_dish)

    # restaurant
    expected_keys = ['owner_id', 'name', 'lat', 'lon', 'phone', 'prec_measures', 'cuisine_type', 'avg_time_of_stay']
    request_dict = dict((k, request_dict[k]) for k in request_dict.keys() if k in expected_keys)
    new_restaurant = Restaurant(**request_dict)
    new_restaurant.capacity = tot_capacity
    new_restaurant.tables = new_tables
    new_restaurant.working_days = new_wds
    new_restaurant.dishes = new_dishes

    db_session.add(new_restaurant)
    db_session.commit()

    return 'Restaurant successfully created'

