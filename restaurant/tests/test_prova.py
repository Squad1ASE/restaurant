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


# --- UNIT TESTS ---
def test_insertDB_restaurant_deleted(test_app):
    app, test_client = test_app

    restaurant_deleted = RestaurantDeleted()
    restaurant_deleted.id = 1
    restaurant_deleted.name = "ciao"
    db_session.add(restaurant_deleted)
    db_session.commit()

    restaurant_deleted = RestaurantDeleted()
    restaurant_deleted.id = 2
    restaurant_deleted.name = "ciao"
    db_session.add(restaurant_deleted)
    db_session.commit()

    restaurant_deleted = RestaurantDeleted()
    restaurant_deleted.id = 3
    restaurant_deleted.name = "ciao"
    db_session.add(restaurant_deleted)
    db_session.commit()

    q = db_session.query(RestaurantDeleted).all()
    print('RestaurantDeleted LEN: ', len(q))
    assert len(q) == 3
    #db_session.commit()

def test_check_02 (test_app):
    app, test_client = test_app
    
    q = db_session.query(RestaurantDeleted).all()
    print('RestaurantDeleted LEN: ', len(q))
    assert len(q) == 0
