from tests.conftest import test_app
from database import db_session, Restaurant, WorkingDay
from sqlalchemy import exc


def _check_working_days(working_day, dict_working_day):
    working_day = working_day.serialize()
    for key in dict_working_day.keys():
        assert working_day[key] == dict_working_day[key]


# --- UNIT TESTS ---
def test_insertDB_working_day(test_app):
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
    incorrect_working_days = [
        dict(restaurant_id = None, day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = 0, day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = -1, day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = 'a', day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = [], day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = ['a'], day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = None, work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 0, work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'ciao', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = ['a'], work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = None),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = []),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [1,2]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['ei']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [[1],[2]]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = ['ei']),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = ['12:00','15:00']),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['12','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['ciao','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [[1,'15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['12:00','15:00','17:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['12:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['19:00','18:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['8:00','10:00'],['12:00','15:00'],['19:00','23:00']])
    ]
    count_assert = 0
    for w in incorrect_working_days:
        try:
            working_day = WorkingDay(**w)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_working_days) == count_assert

    # missing fields
    incorrect_working_days = [
        dict(day = 'monday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, work_shifts = [['12:00','15:00'],['19:00','23:00']]),
        dict(restaurant_id = restaurant.id, day = 'monday')
    ]
    count_assert = 0
    for w in incorrect_working_days:
        working_day = WorkingDay(**w)
        try:
            db_session.add(working_day)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_working_days) == count_assert

    # correct working_days
    correct_working_days = [
        dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['12:00','15:00']]),
        dict(restaurant_id = restaurant.id, day = 'friday', work_shifts = [['12:00','15:00'],['19:00','23:00']]),
    ]
    for idx, w in enumerate(correct_working_days):
        working_day = WorkingDay(**w)
        db_session.add(working_day)
        db_session.commit()
        working_day_to_check = db_session.query(WorkingDay).filter(WorkingDay.restaurant_id == working_day.restaurant_id).filter(WorkingDay.day == working_day.day).first()
        assert working_day_to_check is not None
        _check_working_days(working_day_to_check, correct_working_days[idx])

    # the insertion of the same day for the same restaurant must fail
    w = dict(restaurant_id = restaurant.id, day = 'monday', work_shifts = [['19:00','23:00']])
    working_day = WorkingDay(**w)
    count_assert = 0
    try:
        db_session.add(working_day)
        db_session.commit()
    except (exc.IntegrityError, exc.InvalidRequestError):
        db_session.rollback()
        count_assert += 1
        assert True
    assert count_assert == 1

    # check total working_days
    working_days = db_session.query(WorkingDay).all()
    assert len(working_days) == len(correct_working_days)