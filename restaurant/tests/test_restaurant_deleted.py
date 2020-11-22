from tests.conftest import test_app
from database import db_session, RestaurantDeleted
from sqlalchemy import exc


def _check_restaurants_deleted(restaurant_deleted, dict_restaurant_deleted):
    assert restaurant_deleted.id == dict_restaurant_deleted['id']
    if 'likes_deleted' in dict_restaurant_deleted:
        assert restaurant_deleted.likes_deleted == dict_restaurant_deleted['likes_deleted']
    else:
        assert restaurant_deleted.likes_deleted == False
    if 'reviews_deleted' in dict_restaurant_deleted: 
        assert restaurant_deleted.reviews_deleted == dict_restaurant_deleted['reviews_deleted'] 
    else:
        assert restaurant_deleted.reviews_deleted == False
    if 'reservations_service_notified' in dict_restaurant_deleted:
        assert restaurant_deleted.reservations_service_notified == dict_restaurant_deleted['reservations_service_notified'] 
    else:
        assert restaurant_deleted.reservations_service_notified == False
    assert restaurant_deleted.serialize() is not None


# --- UNIT TESTS ---
def test_insertDB_restaurant_deleted(test_app):
    app, test_client = test_app
    
    # incorrect fields with validators
    incorrect_restaurants_deleted = [
    dict(id=None, name='trial'),
    dict(id=0, name='trial'),
        dict(id=-1, name='trial'),
        dict(id=1, name=None),
        dict(id=1, name=''),
        dict(id=1, name=[]),
        dict(id=1, name=0),
        dict(id=2, name='trial', likes_deleted=1),
        dict(id=2, name='trial', likes_deleted='a'),
        dict(id=2, name='trial', reviews_deleted=1),
        dict(id=2, name='trial', reviews_deleted='a'),
        dict(id=2, name='trial', reservations_service_notified=1),
        dict(id=2, name='trial', reservations_service_notified='a'),
    ]
    count_assert = 0
    for r in incorrect_restaurants_deleted:
        try:
            restaurant_deleted = RestaurantDeleted(**r)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_restaurants_deleted) == count_assert

    # missing mandatory fields
    incorrect_restaurants_deleted = [
        dict(id=1)
    ]
    count_assert = 0
    for r in incorrect_restaurants_deleted:
        restaurant_deleted = RestaurantDeleted(**r)
        try:
            db_session.add(restaurant_deleted)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_restaurants_deleted) == count_assert

    # correct restaurants_deleted
    correct_restaurants_deleted = [
        dict(id=1, name='trial'),
        dict(id=2, name='trial', likes_deleted=False, reviews_deleted=False, reservations_service_notified=False),
        dict(id=3, name='trial', likes_deleted=True, reviews_deleted=True, reservations_service_notified=True),
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()
        restaurant_deleted_to_check = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == restaurant_deleted.id).first()
        assert restaurant_deleted_to_check is not None
        _check_restaurants_deleted(restaurant_deleted_to_check, correct_restaurants_deleted[idx])

    # id already used
    incorrect_restaurants_deleted = [
        dict(id=1, name='trial')
    ]
    count_assert = 0
    for r in incorrect_restaurants_deleted:
        restaurant_deleted = RestaurantDeleted(**r)
        try:
            db_session.add(restaurant_deleted)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_restaurants_deleted) == count_assert

    # check total restaurants_deleted
    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == len(correct_restaurants_deleted)