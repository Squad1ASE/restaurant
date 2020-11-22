from tests.conftest import test_app
from database import db_session, Restaurant, Table, Dish, WorkingDay
from sqlalchemy import exc
import datetime
from datetime import timedelta


def _check_restaurants(restaurant, dict_restaurant):
    restaurant = restaurant.serialize()
    tot_capacity = 0
    for key in dict_restaurant.keys():
        if key in ['tables', 'dishes', 'working_days']:
            for idx, el in enumerate(dict_restaurant[key]):
                serialized = el.serialize()
                for k in serialized:
                    assert restaurant[key][idx][k] == serialized[k]
                if key == 'tables':
                    tot_capacity += serialized['capacity']
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
def test_create_restaurant(test_app):
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
        _check_restaurants(restaurant_to_check, correct_restaurants[idx])

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
        dict(owner_id = 1, name = 'Trial', lat = 'a', lon = None, phone = '3346734121', cuisine_type = ['traditional'],
            capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30, tot_reviews = 0, avg_rating = 0, likes = 0
        ),
        dict(owner_id = 1, name = 'Trial', lat = 'a', lon = 22, phone = '3346734121', cuisine_type = ['traditional'],
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
            print(r)
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