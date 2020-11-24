import connexion
from database import db_session, Restaurant, Table, WorkingDay, Dish, RestaurantDeleted
from flask import request
from sqlalchemy import or_, and_
import json


def create_restaurant():
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
            new_wd = WorkingDay()
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


def get_restaurants():
    owner_id = request.args['owner_id'] if 'owner_id' in request.args else None
    name = request.args['name'] if 'name' in request.args else None
    lat = float(request.args['lat']) if 'lat' in request.args else None
    lon = float(request.args['lon']) if 'lon' in request.args else None

    body = dict(request.args.lists())
    cuisine_types = body['cuisine_type'] if 'cuisine_type' in body else None

    q = db_session.query(Restaurant)
    
    if owner_id is not None:
        q = q.filter(Restaurant.owner_id == owner_id)
    
    if name is not None:
        q = q.filter(Restaurant.name.contains(name))

    if (lat is not None and lon is None) or (lat is None and lon is not None):
        return connexion.problem(400, "Bad Request", "'lat' and 'lon' must be provided together")
    if lat is not None and lon is not None:
        q = q.filter(
            and_(
                and_(Restaurant.lat >= lat - 0.02, Restaurant.lat <= lat + 0.02),
                and_(Restaurant.lon >= lon - 0.02, Restaurant.lon <= lon + 0.02)    
            )
        )

    if cuisine_types is not None:
        allrestaurants_list = []
        for restaurant in q.all():
            for restaurant_cuisine in restaurant.cuisine_type:
                if restaurant_cuisine in cuisine_types:
                    allrestaurants_list.append(restaurant)
                    break
        return [p.serialize() for p in allrestaurants_list]
    else:
        restaurants = q.all()
        return [p.serialize() for p in restaurants]


def delete_restaurants():
    request_dict = request.json

    restaurants = db_session.query(Restaurant).filter(Restaurant.owner_id == request_dict['owner_id']).all()
    
    if len(restaurants) > 0:
        for restaurant in restaurants:
            # update table RestaurantDeleted to ensure that the likes, reviews and  
            # reservations relating to the restaurant are deleted asynchronously
            restaurant_deleted = RestaurantDeleted()
            restaurant_deleted.id = restaurant.id
            restaurant_deleted.name = restaurant.name
            db_session.add(restaurant_deleted)

            # dishes, working days and tables are deleted on cascade
            db_session.delete(restaurant)
        
        db_session.commit()

    return 'Restaurants successfully deleted'


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

    if restaurant.owner_id != request_dict['owner_id']:
        return connexion.problem(403, "Forbidden", "Specified owner_id is not the restaurant owner")

    dishes = request_dict.pop('dishes', None)
    if dishes is not None:
        new_dishes = []
        for dish in dishes:
            new_dish = Dish()
            new_dish.name = dish['name'] 
            new_dish.price = dish['price'] 
            new_dish.ingredients = dish['ingredients'] 
            new_dishes.append(new_dish)
        restaurant.dishes = new_dishes

    new_phone = request_dict.pop('phone', None)
    if new_phone is not None:
        restaurant.phone = new_phone

    if new_phone is not None or dishes is not None:
        db_session.commit()

    return 'Restaurant successfully edited'


def delete_restaurant(restaurant_id):
    request_dict = request.json
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if restaurant is None:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")

    if restaurant.owner_id != request_dict['owner_id']:
        return connexion.problem(403, "Forbidden", "Specified owner_id is not the restaurant owner")

    # update table RestaurantDeleted to ensure that the likes, reviews and  
    # reservations relating to the restaurant are deleted asynchronously
    restaurant_deleted = RestaurantDeleted()
    restaurant_deleted.id = restaurant_id
    restaurant_deleted.name = restaurant.name
    db_session.add(restaurant_deleted)

    # dishes, working days and tables are deleted on cascade
    db_session.delete(restaurant)
    db_session.commit()

    return 'Restaurant successfully deleted'