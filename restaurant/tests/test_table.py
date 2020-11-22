from tests.conftest import test_app
from database import db_session, Restaurant, Table
from sqlalchemy import exc


def _check_tables(table, dict_table):
    table = table.serialize()
    for key in dict_table.keys():
        assert table[key] == dict_table[key]


 # --- UNIT TESTS ---
def test_insertDB_table(test_app):
    app, test_client = test_app
   
    # create a restaurant to testing table insertions
    restaurant_dict = dict(
        owner_id=1, name='Restaurant 1', lat=43.7216621, lon=10.4083723, phone='111111', capacity=10,
        cuisine_type=["italian", "traditional"], prec_measures='leggeX', avg_time_of_stay=30
    )
    restaurant = Restaurant(**restaurant_dict)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # incorrect mandatory fields with validators
    incorrect_tables = [
        dict(restaurant_id = None, capacity = 1, name = 'table'),
        dict(restaurant_id = 0, capacity = 1, name = 'table'),
        dict(restaurant_id = -1, capacity = 1, name = 'table'),
        dict(restaurant_id = 'a', capacity = 1, name = 'table'),
        dict(restaurant_id = [], capacity = 1, name = 'table'),
        dict(restaurant_id = ['a'], capacity = 1, name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = None, name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = 0, name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = -1, name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = 'a', name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = [], name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = ['a'], name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = 1, name = None),
        dict(restaurant_id = restaurant.id, capacity = 1, name = ''),
        dict(restaurant_id = restaurant.id, capacity = 1, name = []),
        dict(restaurant_id = restaurant.id, capacity = 1, name = ['a']),
    ]
    count_assert = 0
    for t in incorrect_tables:
        try:
            table = Table(**t)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_tables) == count_assert

    # missing fields
    incorrect_tables = [
        dict(capacity = 1, name = 'table'),
        dict(restaurant_id = restaurant.id, name = 'table'),
        dict(restaurant_id = restaurant.id, capacity = 1)
    ]
    count_assert = 0
    for t in incorrect_tables:
        table = Table(**t)
        try:
            db_session.add(table)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_tables) == count_assert

    # correct tables
    correct_tables = [
        dict(restaurant_id = restaurant.id, capacity = 1, name = 'c'),
        dict(restaurant_id = restaurant.id, capacity = 30, name = 'big table'),
    ]
    for idx, t in enumerate(correct_tables):
        table = Table(**t)
        db_session.add(table)
        db_session.commit()
        table_to_check = db_session.query(Table).filter(Table.id == table.id).first()
        assert table_to_check is not None
        _check_tables(table_to_check, correct_tables[idx])

    # check total tables
    tables = db_session.query(Table).all()
    assert len(tables) == len(correct_tables)