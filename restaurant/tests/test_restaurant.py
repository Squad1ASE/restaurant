from tests.conftest import test_app
from database import db_session, Restaurant, Table, Dish, WorkingDay, RestaurantDeleted
from sqlalchemy import exc
from tests.utilities import *
import datetime
from datetime import timedelta


def _check_restaurants(restaurant, dict_restaurant, to_serialize=False):
    if not isinstance(restaurant, dict): 
        restaurant = restaurant.serialize()
    tot_capacity = 0
    for key in dict_restaurant.keys():
        if key in ['tables', 'dishes', 'working_days']:
            if to_serialize:
                dict_restaurant[key] = [p.serialize() for p in dict_restaurant[key]]
            if key in ['tables', 'dishes']:
                dict_restaurant[key] = sorted(dict_restaurant[key], key=lambda k: k['name']) 
                restaurant[key] = sorted(restaurant[key], key=lambda k: k['name']) 
            else:
                dict_restaurant[key] = sorted(dict_restaurant[key], key=lambda k: k['day']) 
                restaurant[key] = sorted(restaurant[key], key=lambda k: k['day']) 
            for idx, el in enumerate(dict_restaurant[key]):
                for k in el:
                    assert restaurant[key][idx][k] == el[k]
                if key == 'tables':
                    tot_capacity += el['capacity']
        else:
            assert restaurant[key] == dict_restaurant[key]
    if 'capacity' not in dict_restaurant:
        assert restaurant['capacity'] == tot_capacity
    if 'tot_reviews' not in dict_restaurant:
        assert restaurant['tot_reviews'] == 0
    if 'avg_rating' not in dict_restaurant:
        assert restaurant['avg_rating'] == 0
    if 'likes' not in dict_restaurant:
        assert restaurant['likes'] == 0


# --- UNIT TESTS ---
def test_insertDB_restaurant(test_app):
    app, test_client = test_app

    tot_correct_restaurants = 0
    tot_correct_tables = 0
    tot_correct_dishes = 0

    tables = [
        Table(**dict(capacity = 2, name = 'yellow')),
        Table(**dict(capacity = 5, name = 'blue'))
    ]
    dishes = [
        Dish(**dict(name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella')),
        Dish(**dict(name = 'pasta', price = 6.0, ingredients = 'mozzarella')),
    ]
    working_days = [
        WorkingDay(**dict(day = 'friday', work_shifts = [['12:00','15:00'],['19:00','23:00']])),
        WorkingDay(**dict(day = 'saturday', work_shifts = [['12:00','15:00'],['19:00','23:00']])),
    ]

    # correct restaurants pt1
    correct_restaurants = [
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0,
            tables = tables, dishes = dishes, working_days = working_days
        ),
        dict(owner_id = 1, name = 'T', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional','italian'],
            capacity = 1, prec_measures = '',avg_time_of_stay = 15, tables = [tables[0]], dishes = [dishes[0]], working_days = [working_days[0]]
        ),
        dict(owner_id = 1, name = 'T', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional','italian'],
            capacity = 1, prec_measures = '',avg_time_of_stay = 15
        )
    ]
    for idx, r in enumerate(correct_restaurants):
        restaurant = Restaurant(**r)
        db_session.add(restaurant)
        db_session.commit()

        restaurant_to_check = db_session.query(Restaurant).filter(Restaurant.id == restaurant.id).first()
        assert restaurant_to_check is not None
        _check_restaurants(restaurant_to_check, correct_restaurants[idx], True)

    tot_correct_restaurants += len(correct_restaurants)


    # incorrect restaurants pt1 - fail check validators
    incorrect_restaurants = [
        # owner_id
        dict(owner_id = None, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 0, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = -1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 'a', name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = ['a'], name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = [], name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # name
        dict(owner_id = 1, name = None, lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = '', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 1, lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = [], lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = ['a'], lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # lat
        dict(owner_id = 1, name = 'Trial', lat = 'a', lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = None, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = [], lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = ['a'], lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # lon
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = None, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 'a', phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = [], phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = ['a'], phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # phone
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = None, cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = 3, cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = ['a'], cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = [], cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # cuisine_type
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = None,
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = [],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = 'traditional',
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditionalll'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = 2,
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # capacity
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = None, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 0, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = -1, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 'a', prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = [], prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = ['a'], prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # prec_measures
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = None,avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 2,avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = [],avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = ['a'],avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # avg_time_of_stay
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 14, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = -1, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 0, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = None, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 'a', tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = ['a'], tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = [], tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        # tot_reviews
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = None, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = -1, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 'a', avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = [], avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = ['a'], avg_rating = 0, likes = 0
        ),
        # avg_rating
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = -1, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 5.1, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = -0.1, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = None, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 'a', likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = [], likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = ['a'], likes = 0
        ),
        # likes
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = None
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = -1
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 'a'
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = []
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = ['a']
        )
    ]
    count_assert = 0
    for r in incorrect_restaurants:
        try:
            restaurant = Restaurant(**r)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_restaurants) == count_assert
    

    # incorrect restaurants pt2 - missing mandatory fields
    incorrect_restaurants = [
        dict(name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121',
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            prec_measures = 'leggeX',avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, avg_time_of_stay = 30
        ),
        dict(owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX'
        )
    ]
    count_assert = 0
    for r in incorrect_restaurants:
        restaurant = Restaurant(**r)
        try:
            db_session.add(restaurant)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_restaurants) == count_assert

    #check total restaurants
    restaurants = db_session.query(Restaurant).all()
    assert len(restaurants) == tot_correct_restaurants


# --- COMPONENT TESTS ---
def test_create_restaurant(test_app):
    app, test_client = test_app

    tot_correct_tables = 0
    tot_correct_dishes = 0
    tot_correct_wds = 0

    # correct restaurants
    for idx, r in enumerate(restaurant_examples):
        assert create_restaurant_by_API(test_client, r).status_code == 200

        tot_correct_tables += len(r['tables'])
        tot_correct_dishes += len(r['dishes'])
        tot_correct_wds += len(r['working_days'])

        # assuming all restaurants' name are distinct in restaurant_examples
        restaurant_to_check = db_session.query(Restaurant).filter(Restaurant.name == r['name']).first()
        assert restaurant_to_check is not None
        _check_restaurants(restaurant_to_check, r)

    
    # incorrect restaurants
    incorrect_restaurants = [
        # fields that must not be present are
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)], id=2,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)], capacity=30,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)], tot_reviews=1,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)], avg_rating=1,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)], likes=1,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # incorrect restaurant fields
        # owner_id
        dict(name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=None, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=0, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=-1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id='a', name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=['a'], name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=[], name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # name
        dict(owner_id=1, lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name=None, lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name=1, lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name=[], lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name=['a'], lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # lat
        dict(owner_id=1, name='Restaurant 1', lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat='a', lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=None, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=[], lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=['a'], lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # lon
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=None, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon='a', phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=[], phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=['a'], phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # phone
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609,
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone=None,  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone=3,  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone=['a'],  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone=[],  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # cuisine_type
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=None, prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=[], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type="italian", prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italiannnnn"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=2, prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # prec_measures
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures=None, avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures=2, avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures=[], avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures=['a'], avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # avg_time_of_stay
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX',
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=14,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=-1,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=0,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=None,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay='a',
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=['a'],
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=[],
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # incorrect tables fields
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict()],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=['yellow',3],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow')],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name=None,capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name=2,capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name=[],capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name=['a'],capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=None)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=0)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=-1)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=['a'])],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity='a')],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=[])],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(restaurant_id=2,name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(id=3,name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        # incorrect dishes fields
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict()],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=['pizza',4.5,'tomato,mozzarella'],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5)],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name=None,price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name=2,price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name=[],price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name=['a'],price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=0,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=-1,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=None,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price='a',ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=[],ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=['a'],ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients=None)],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients=3)],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients=[])],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients=['a'])],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(id=3,name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(restaurant_id=2,name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "23:59"]])]
        ),

        # incorrect working days fields
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=None
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict()]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday')]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day=None,work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='',work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day=3,work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day=['a'],work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day=[],work_shifts=[["00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=None)]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[[1, 2]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["10:01", "12:59"],["16:01", "19:59"],["21:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["15:00", "15:00"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01 ", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:010", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[[" 00:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["000:01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00-01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00/01", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["10:00", "10:00"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["10:01", "10:00"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["12:01", "14:59"],["14:59", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["12:01", "14:59"],["14:58", "23:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(restaurant_id=2,day='monday',work_shifts=[["00:01", "14:59"]])]
        ),
        dict(owner_id=1, name='Restaurant 1', lat=43.4702169, lon=11.152609, phone='333333',  
            cuisine_type=["italian", "chinese"], prec_measures='lawX', avg_time_of_stay=15,
            tables=[dict(name='yellow',capacity=3)],
            dishes=[dict(name='pizza',price=4.5,ingredients='tomato,mozzarella')],
            working_days=[dict(day='monday',work_shifts=[["00:01", "14:59"]]),dict(day='monday',work_shifts=[["00:01", "14:59"]])]
        )
    ]
    for r in incorrect_restaurants:
        assert create_restaurant_by_API(test_client, r).status_code == 400
    

    #check total restaurants/tables/dishes/working_days
    restaurants = db_session.query(Restaurant).all()
    assert len(restaurants) == len(restaurant_examples)
    tables = db_session.query(Table).all()
    assert len(tables) == tot_correct_tables
    dishes = db_session.query(Dish).all()
    assert len(dishes) == tot_correct_dishes
    wds = db_session.query(WorkingDay).all()
    assert len(wds) == tot_correct_wds


def test_get_restaurants(test_app):
    app, test_client = test_app
    
    # empty get 
    response = get_restaurants_by_API(test_client)
    assert response.status_code == 200
    assert response.json == []
    
    # create some restaurants
    correct_restaurants = restaurant_examples
    for idx, r in enumerate(correct_restaurants):
        assert create_restaurant_by_API(test_client, r).status_code == 200
    
    # correct get 
    response = get_restaurants_by_API(test_client)
    assert response.status_code == 200
    restaurants = response.json
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # bad query parameters
    assert get_restaurants_by_API(test_client, 0).status_code == 400
    assert get_restaurants_by_API(test_client, -1).status_code == 400
    assert get_restaurants_by_API(test_client, 'a').status_code == 400
    assert get_restaurants_by_API(test_client, []).status_code == 400
    assert get_restaurants_by_API(test_client, ['a']).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, 1).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, 'a').status_code == 400
    assert get_restaurants_by_API(test_client, None, None, []).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, ['a']).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, None, 1).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, None, 'a').status_code == 400
    assert get_restaurants_by_API(test_client, None, None, None, []).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, None, ['a']).status_code == 400
    assert get_restaurants_by_API(test_client, None, None, 1, 'a').status_code == 400
    assert get_restaurants_by_API(test_client, None, None, 'a', 1).status_code == 400
    
    # correct query parameters - owner id
    correct_restaurants = restaurant_examples
    owner_id = correct_restaurants[0]['owner_id']
    response = get_restaurants_by_API(test_client, owner_id)
    assert response.status_code == 200
    restaurants = response.json
    correct_restaurants = [p for p in correct_restaurants if p['owner_id'] == owner_id]
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # correct query parameters - name
    correct_restaurants = restaurant_examples
    response = get_restaurants_by_API(test_client, None, '-')
    assert response.status_code == 200
    restaurants = response.json
    correct_restaurants = [p for p in correct_restaurants if '-' in p['name']]
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # correct query parameters - lat and lon
    # the first two restaurants in restaurant_examples should be relatively close
    correct_restaurants = [restaurant_examples[0], restaurant_examples[1]]
    response = get_restaurants_by_API(test_client, None, None, restaurant_examples[0]['lat'], restaurant_examples[0]['lon'])
    assert response.status_code == 200
    restaurants = response.json
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # correct query parameters - all filters
    response = get_restaurants_by_API(test_client, restaurant_examples[0]['owner_id'], restaurant_examples[0]['name'], restaurant_examples[0]['lat'], restaurant_examples[0]['lon'])
    assert response.status_code == 200
    restaurants = response.json
    assert len(restaurants) == 1
    _check_restaurants(restaurants[0], restaurant_examples[0])


def test_delete_restaurants(test_app):
    app, test_client = test_app

    # create some restaurants
    correct_restaurants = restaurant_examples
    for idx, r in enumerate(correct_restaurants):
        assert create_restaurant_by_API(test_client, r).status_code == 200
    
    # incorrect body json
    assert test_client.delete('/restaurants', json=dict(owner_id=0), follow_redirects=True).status_code == 400
    assert test_client.delete('/restaurants', json=dict(owner_id=-1), follow_redirects=True).status_code == 400
    assert test_client.delete('/restaurants', json=dict(owner_id='a'), follow_redirects=True).status_code == 400
    assert test_client.delete('/restaurants', json=dict(owner_id=[]), follow_redirects=True).status_code == 400
    assert test_client.delete('/restaurants', json=dict(), follow_redirects=True).status_code == 400
    assert test_client.delete('/restaurants', follow_redirects=True).status_code == 400

    # correct - pt1
    owner_id = restaurant_examples[0]['owner_id']
    assert test_client.delete('/restaurants', json=dict(owner_id=owner_id), follow_redirects=True).status_code == 200

    deleted_restaurants = [p for p in restaurant_examples if p['owner_id'] == owner_id]
    remaining_restaurants = len(restaurant_examples) - len(deleted_restaurants)

    remaining_restaurants_db = db_session.query(Restaurant).all()
    assert len(remaining_restaurants_db) == remaining_restaurants
    remaining_tables, remaining_dishes, remaining_wds = 0, 0, 0
    for r in remaining_restaurants_db:
        remaining_tables += len(r.tables)
        remaining_dishes += len(r.dishes)
        remaining_wds += len(r.working_days)
    
    q = db_session.query(Table).all()
    assert len(q) == remaining_tables
    q = db_session.query(Dish).all()
    assert len(q) == remaining_dishes
    q = db_session.query(WorkingDay).all()
    assert len(q) == remaining_wds
    deleted_restaurants_db = db_session.query(RestaurantDeleted).all()
    assert len(deleted_restaurants_db) == len(deleted_restaurants)

    # correct - pt2 owner_id without restaurants
    assert test_client.delete('/restaurants', json=dict(owner_id=9999), follow_redirects=True).status_code == 200

    # correct - pt3
    # it should also work with an additional meaningless body parameter
    owner_id = restaurant_examples[1]['owner_id']
    assert test_client.delete('/restaurants', json=dict(owner_id=owner_id, trial='hello'), follow_redirects=True).status_code == 200
    # by deleting the restaurants of the owner_id of the first two restaurants 
    # in 'restaurant_examples' all the restaurants should be deleted
    q = db_session.query(Restaurant).all()
    assert len(q) == 0
    q = db_session.query(Table).all()
    assert len(q) == 0
    q = db_session.query(Dish).all()
    assert len(q) == 0
    q = db_session.query(WorkingDay).all()
    assert len(q) == 0
    deleted_restaurants_db = db_session.query(RestaurantDeleted).all()
    assert len(deleted_restaurants_db) == len(restaurant_examples)


def test_get_restaurant(test_app):
    app, test_client = test_app
    
    # incorrect get - restaurant_id not exists
    assert get_restaurant_by_API(test_client, 1).status_code == 404
    
    # incorrect get - restaurant_id incorrect
    assert get_restaurant_by_API(test_client, 0).status_code == 400
    assert get_restaurant_by_API(test_client, -1).status_code == 404
    assert get_restaurant_by_API(test_client, 'a').status_code == 404
    assert get_restaurant_by_API(test_client, ['a']).status_code == 404
    assert get_restaurant_by_API(test_client, []).status_code == 404

    # create some restaurants
    correct_restaurants = restaurant_examples
    for idx, r in enumerate(correct_restaurants):
        assert create_restaurant_by_API(test_client, r).status_code == 200
    
    # correct get 
    for idx, r in enumerate(correct_restaurants):
        response = get_restaurant_by_API(test_client, idx+1)
        assert response.status_code == 200
        _check_restaurants(response.json, r)


def test_edit_restaurant(test_app):
    app, test_client = test_app
    
    owner_id = restaurant_examples[0]['owner_id']
    edit_dict = dict(
        owner_id=owner_id,
        phone='3243243434',
        dishes=[
            dict(name='pizza2',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta2',price=6.5,ingredients='tomato'),
            dict(name='pizza3',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta3',price=6.5,ingredients='tomato')
        ]
    )

    # incorrect edit - restaurant_id not exists
    assert edit_restaurant_by_API(test_client, 1, edit_dict).status_code == 404
    
    # create one restaurant
    assert create_restaurant_by_API(test_client, restaurant_examples[0]).status_code == 200

    # incorrect edit - incorrect restaurant_id
    assert edit_restaurant_by_API(test_client, 0, edit_dict).status_code == 400
    assert edit_restaurant_by_API(test_client, -1, edit_dict).status_code == 404
    assert edit_restaurant_by_API(test_client, 'a', edit_dict).status_code == 404
    assert edit_restaurant_by_API(test_client, ['a'], edit_dict).status_code == 404
    assert edit_restaurant_by_API(test_client, [], edit_dict).status_code == 404

    # incorrect edit - incorrect restaurant_id
    incorrect_dicts = [
        dict(phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id),
        dict(owner_id=owner_id, phone='3243243434', dishes=[]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict()]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name=None,price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='',price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name=1,price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name=[],price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name=['a'],price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=None,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=0,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=-1,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price='a',ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=[],ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=['a'],ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients=None)]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients='')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients=2)]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients=[])]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5,ingredients=['a'])]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(price=4.5,ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',ingredients='tomato,mozzarella')]),
        dict(owner_id=owner_id, phone='3243243434', dishes=[dict(name='pizza2',price=4.5)])
    ]
    for d in incorrect_dicts:
        assert edit_restaurant_by_API(test_client, 1, d).status_code == 400

    #incorrect edit - owner_id is not the restaurant's owner
    d = dict(
        owner_id=9999, phone='3243243434',
        dishes=[dict(name='pizza2',price=4.5,ingredients='tomato,mozzarella')]
    )
    assert edit_restaurant_by_API(test_client, 1, d).status_code == 403

    # correct pt1
    restaurant_edited = restaurant_examples[0]
    restaurant_edited['phone'] = edit_dict['phone']
    restaurant_edited['dishes'] = edit_dict['dishes']
    assert edit_restaurant_by_API(test_client, 1, edit_dict).status_code == 200
    q = db_session.query(Dish).all()
    assert len(q) == len(edit_dict['dishes'])
    restaurant = db_session.query(Restaurant).first()
    _check_restaurants(restaurant, restaurant_edited)

    # correct pt2 - ok but meaningless
    assert edit_restaurant_by_API(test_client, 1, dict(owner_id=owner_id, trial='aaaa')).status_code == 200
    q = db_session.query(Dish).all()
    assert len(q) == len(edit_dict['dishes'])
    restaurant = db_session.query(Restaurant).first()
    _check_restaurants(restaurant, restaurant_edited)

    # correct pt3 - only phone
    restaurant_edited['phone'] = '111'
    assert edit_restaurant_by_API(test_client, 1, dict(owner_id=owner_id,phone='111')).status_code == 200
    q = db_session.query(Dish).all()
    assert len(q) == len(edit_dict['dishes'])
    restaurant = db_session.query(Restaurant).first()
    _check_restaurants(restaurant, restaurant_edited)

    # correct pt3 - only dishes
    restaurant_edited['dishes'] = [dict(name='pizza2',price=4.5,ingredients='tomato,mozzarella')]
    assert edit_restaurant_by_API(test_client, 1, dict(owner_id=owner_id,dishes=restaurant_edited['dishes'])).status_code == 200
    q = db_session.query(Dish).all()
    assert len(q) == len(restaurant_edited['dishes'])
    restaurant = db_session.query(Restaurant).first()
    _check_restaurants(restaurant, restaurant_edited)
    
    # correct pt4 - phone, dishes and an additional properties that shouldn't be edited
    edit_dict = dict(
        owner_id=owner_id,
        phone='3243243434',
        dishes=[
            dict(name='pizza2',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta2',price=6.5,ingredients='tomato'),
            dict(name='pizza3',price=4.5,ingredients='tomato,mozzarella'), 
            dict(name='pasta3',price=6.5,ingredients='tomato')
        ],
        capcity=100
    )
    restaurant_edited['phone'] = edit_dict['phone']
    restaurant_edited['dishes'] = edit_dict['dishes']
    assert edit_restaurant_by_API(test_client, 1, edit_dict).status_code == 200
    q = db_session.query(Dish).all()
    assert len(q) == len(edit_dict['dishes'])
    restaurant = db_session.query(Restaurant).first()
    _check_restaurants(restaurant, restaurant_edited)


def test_delete_restaurant(test_app):
    app, test_client = test_app

    # incorrect delete - restaurant_id not exists
    assert delete_restaurant_by_API(test_client, 1, 1).status_code == 404
    
    # create some restaurants
    correct_restaurants = restaurant_examples
    for idx, r in enumerate(correct_restaurants):
        assert create_restaurant_by_API(test_client, r).status_code == 200
    
    # incorrect body json
    assert delete_restaurant_by_API(test_client, 1, 0).status_code == 400
    assert delete_restaurant_by_API(test_client, 1, -1).status_code == 400
    assert delete_restaurant_by_API(test_client, 1, 'a').status_code == 400
    assert delete_restaurant_by_API(test_client, 1, []).status_code == 400
    assert delete_restaurant_by_API(test_client, 1, None).status_code == 400
    assert delete_restaurant_by_API(test_client, 1, ['a']).status_code == 400
    assert test_client.delete('/restaurants/1', follow_redirects=True).status_code == 400

    #incorrect edit - owner_id is not the restaurant's owner
    assert delete_restaurant_by_API(test_client, 1, 9999).status_code == 403

    # correct - pt1
    owner_id = restaurant_examples[0]['owner_id']
    assert delete_restaurant_by_API(test_client, 1, owner_id).status_code == 200

    deleted_restaurants = [restaurant_examples[0]]
    remaining_restaurants = len(restaurant_examples) - len(deleted_restaurants)

    remaining_restaurants_db = db_session.query(Restaurant).all()
    assert len(remaining_restaurants_db) == remaining_restaurants
    remaining_tables, remaining_dishes, remaining_wds = 0, 0, 0
    for r in remaining_restaurants_db:
        remaining_tables += len(r.tables)
        remaining_dishes += len(r.dishes)
        remaining_wds += len(r.working_days)
    
    q = db_session.query(Table).all()
    assert len(q) == remaining_tables
    q = db_session.query(Dish).all()
    assert len(q) == remaining_dishes
    q = db_session.query(WorkingDay).all()
    assert len(q) == remaining_wds
    deleted_restaurants_db = db_session.query(RestaurantDeleted).all()
    assert len(deleted_restaurants_db) == len(deleted_restaurants)

    # correct - pt2 
    # it should also work with an additional meaningless body parameter
    owner_id = restaurant_examples[1]['owner_id']
    assert test_client.delete('/restaurants/2', json=dict(owner_id=owner_id, trial='hello'), follow_redirects=True).status_code == 200
    
    deleted_restaurants = [restaurant_examples[0],restaurant_examples[1]]
    remaining_restaurants = len(restaurant_examples) - len(deleted_restaurants)

    remaining_restaurants_db = db_session.query(Restaurant).all()
    assert len(remaining_restaurants_db) == remaining_restaurants
    remaining_tables, remaining_dishes, remaining_wds = 0, 0, 0
    for r in remaining_restaurants_db:
        remaining_tables += len(r.tables)
        remaining_dishes += len(r.dishes)
        remaining_wds += len(r.working_days)
    
    q = db_session.query(Table).all()
    assert len(q) == remaining_tables
    q = db_session.query(Dish).all()
    assert len(q) == remaining_dishes
    q = db_session.query(WorkingDay).all()
    assert len(q) == remaining_wds
    deleted_restaurants_db = db_session.query(RestaurantDeleted).all()
    assert len(deleted_restaurants_db) == len(deleted_restaurants)