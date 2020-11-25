from tests.conftest import test_app
from database import db_session, Restaurant, Dish
from sqlalchemy import exc


def _check_dishes(dish, dict_dish):
    dish = dish.serialize()
    for key in dict_dish.keys():
        assert dish[key] == dict_dish[key]


def test_insertDB_dish(test_app):
    app, test_client = test_app

    restaurant_dict = dict(
        owner_id=1, name='Restaurant 1', lat=43.7216621, lon=10.4083723, phone='111111', capacity=10,
        cuisine_type=["italian", "traditional"], prec_measures='leggeX', avg_time_of_stay=30
    )
    restaurant = Restaurant(**restaurant_dict)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # incorrect fields with validators
    incorrect_dishes = [
        dict(restaurant_id = None, name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = 0, name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = -1, name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = ['a'], name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = [], name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = 'a', name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = None, price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = '', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 1, price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = ['a'], price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = None, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = -1, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 'a', ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = [], ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = ['a'], ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = None),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = ''),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = []),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = 1),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = ['a'])
    ]
    count_assert = 0
    for d in incorrect_dishes:
        try:
            dish = Dish(**d)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_dishes) == count_assert


    # missing mandatory fields
    incorrect_dishes = [
        dict(name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0)
    ]
    count_assert = 0
    for d in incorrect_dishes:
        dish = Dish(**d)
        try:
            db_session.add(dish)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_dishes) == count_assert

    # correct dishes
    correct_dishes = [
        dict(restaurant_id = restaurant.id, name = 'pizza', price = 4.0, ingredients = 'pomodoro, mozzarella'),
        dict(restaurant_id = restaurant.id, name = 'p', price = 0.1, ingredients = 'p')
    ]
    for idx, d in enumerate(correct_dishes):
        dish = Dish(**d)
        db_session.add(dish)
        db_session.commit()
        dish_to_check = db_session.query(Dish).filter(Dish.id == dish.id).first()
        assert dish_to_check is not None
        _check_dishes(dish_to_check, correct_dishes[idx])

    # check total dishes
    dishes = db_session.query(Dish).all()
    assert len(dishes) == len(correct_dishes)