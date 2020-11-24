from tests.conftest import test_app
from database import db_session, Restaurant, Review
from sqlalchemy import exc
from tests.utilities import get_reviews_by_API, mocked_reservations
import datetime
from unittest import mock
from unittest.mock import patch
import requests


def _check_reviews(review, dict_review):
    if not isinstance(review, dict): 
        review = review.serialize()
    for key in dict_review.keys():
        if key == 'date':
            assert review['date'] == dict_review['date'].strftime("%d/%m/%Y")
        elif key == 'marked':
            continue
        else:
            assert review[key] == dict_review[key]


def test_insertDB_review(test_app):
    app, test_client = test_app

    # create a restaurant to test reviews
    correct_restaurants = dict(
        owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()

    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    now = datetime.datetime.now()

    # incorrect reviews pt1 - fail check validators
    incorrect_reviews = [
        dict(
            user_id=None, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=0, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=-1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id='a', restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=[], restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=['a'], restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=None, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=0, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=-1, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id='a', rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=['a'], rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=0,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3.5,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=6,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating='a',
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=[],
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=['a'],
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=None,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment=None, date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment=2, date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment=[], date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment=['a'], date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=None, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=2, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date='a', marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=[], marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=['a'], marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=None
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=2
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked='a'
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=[]
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=['a']
        )
    ]
    count_assert = 0
    for r in incorrect_reviews:
        try:
            review = Review(**r)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_reviews) == count_assert
    

    # incorrect reviews pt2 - missing mandatory fields
    incorrect_reviews = [
        dict(
            restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            date=now, marked=False
        ),
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', marked=False
        )
    ]
    count_assert = 0
    for r in incorrect_reviews:
        review = Review(**r)
        try:
            db_session.add(review)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_reviews) == count_assert

    # correct reviews
    correct_reviews = [
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=2, restaurant_id=restaurant.id, rating=1,
            comment='g', date=now
        ),
        dict(
            user_id=3, restaurant_id=restaurant.id, rating=5,
            comment='good!', date=now, marked=False
        )
    ]
    for idx, r in enumerate(correct_reviews):
        review = Review(**r)
        db_session.add(review)
        db_session.commit()
        review_to_check = db_session.query(Review).filter(Review.user_id == correct_reviews[idx]['user_id']).first()
        assert review_to_check is not None
        _check_reviews(review_to_check, correct_reviews[idx])

    # incorrect reviews pt3 - a user cannot review the same restaurant multiple times
    incorrect_reviews = [
        dict(
            user_id=1, restaurant_id=restaurant.id, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=2, restaurant_id=restaurant.id, rating=1,
            comment='g', date=now
        )
    ]
    count_assert = 0
    for r in incorrect_reviews:
        review = Review(**r)
        try:
            db_session.add(review)
            db_session.commit()
        except Exception:
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_reviews) == count_assert

    # check total reviews
    reviews = db_session.query(Review).all()
    assert len(reviews) == len(correct_reviews)


@patch('views.review.requests.get')
def test_create_review(mock1, test_app):
    app, test_client = test_app

    # mocked reservations with at least one element
    ok_mock = mock.MagicMock()
    type(ok_mock).status_code = mock.PropertyMock(return_value=200)
    ok_mock.json.return_value = mocked_reservations
    mock1.return_value = ok_mock

    # incorrect create review - restaurant_id not exists
    correct_body = dict(user_id=1, restaurant_id=1, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 404
    
    # create a restaurant to test reviews
    correct_restaurants = dict(
        owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # bad body parameters
    incorrect_bodies = [
        dict(restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=1, comment='good!', rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!'),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', trial=3),
        dict(user_id=None, restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=0, restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=-1, restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id='a', restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=[], restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=['a'], restaurant_id=restaurant.id, comment='good!', rating=3),
        dict(user_id=1, restaurant_id=None, comment='good!', rating=3),
        dict(user_id=1, restaurant_id=0, comment='good!', rating=3),
        dict(user_id=1, restaurant_id=-1, comment='good!', rating=3),
        dict(user_id=1, restaurant_id='a', comment='good!', rating=3),
        dict(user_id=1, restaurant_id=[], comment='good!', rating=3),
        dict(user_id=1, restaurant_id=['a'], comment='good!', rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment=None, rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment='', rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment=2, rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment=[], rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment=['a'], rating=3),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=None),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=0),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=6),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=3.5),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=-1),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating='a'),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=[]),
        dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=['a'])
    ]
    for r in incorrect_bodies:
        assert test_client.put('/reviews', json=r, follow_redirects=True).status_code == 400

    # correct create review pt1
    correct_body = dict(user_id=1, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 200
    review_to_check = db_session.query(Review).filter(Review.user_id == 1).first()
    assert review_to_check is not None
    _check_reviews(review_to_check, correct_body)

    # correct create review pt2
    correct_body = dict(user_id=2, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 200
    review_to_check = db_session.query(Review).filter(Review.user_id == 2).first()
    assert review_to_check is not None
    _check_reviews(review_to_check, correct_body)

    # attempt to put review with the same user
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 403

    # empty mocked reservations - attempt to review without making a reservation first
    ok_mock.json.return_value = []
    mock1.return_value = ok_mock
    correct_body = dict(user_id=5, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 403

    # Reservations service responds with error - pt1
    not_ok_mock = mock.MagicMock()
    type(not_ok_mock).status_code = mock.PropertyMock(return_value=404)
    not_ok_mock.json.return_value = mocked_reservations
    mock1.return_value = not_ok_mock
    correct_body = dict(user_id=5, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 500

    # Reservations service responds with error - pt2
    not_ok_mock = mock.MagicMock()
    type(not_ok_mock).status_code = mock.PropertyMock(return_value=500)
    not_ok_mock.json.return_value = mocked_reservations
    mock1.return_value = not_ok_mock
    correct_body = dict(user_id=5, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 500

    # check total reviews
    reviews = db_session.query(Review).all()
    assert len(reviews) == 2


def test_create_review_timeout_eceptions(test_app):
    app, test_client = test_app

    # create a restaurant to test reviews
    correct_restaurants = dict(
        owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # Reservations service raise exception
    correct_body = dict(user_id=5, restaurant_id=restaurant.id, comment='good!', rating=3)
    assert test_client.put('/reviews', json=correct_body, follow_redirects=True).status_code == 500


def test_get_reviews(test_app):
    app, test_client = test_app
    
    # empty get 
    response = get_reviews_by_API(test_client)
    assert response.status_code == 200
    assert response.json == []
    
    # create two restaurant to test reviews
    correct_restaurants = dict(
        owner_id = 123, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    correct_restaurants = dict(
        owner_id = 122, name = 'Trial - 2', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)

    db_session.commit()
    restaurant = db_session.query(Restaurant).all()
    assert len(restaurant) == 2

    # correct reviews
    now = datetime.datetime.now()
    original_correct_reviews = [
        dict(
            user_id=1, restaurant_id=1, rating=3,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=2, restaurant_id=1, rating=1,
            comment='g', date=now
        ),
        dict(
            user_id=1, restaurant_id=2, rating=5,
            comment='mhhh!', date=now, marked=False
        )
    ]
    for idx, r in enumerate(original_correct_reviews):
        review = Review(**r)
        db_session.add(review)
    db_session.commit()

    # correct get 
    correct_reviews = original_correct_reviews
    response = get_reviews_by_API(test_client)
    assert response.status_code == 200
    reviews = response.json
    assert len(correct_reviews) == len(reviews)
    correct_reviews = sorted(correct_reviews, key=lambda k: k['comment']) 
    reviews = sorted(reviews, key=lambda k: k['comment']) 
    for idx, r in enumerate(correct_reviews):
        _check_reviews(reviews[idx], r)

    # bad query parameters
    assert get_reviews_by_API(test_client, 0).status_code == 400
    assert get_reviews_by_API(test_client, -1).status_code == 400
    assert get_reviews_by_API(test_client, 'a').status_code == 400
    assert get_reviews_by_API(test_client, []).status_code == 400
    assert get_reviews_by_API(test_client, ['a']).status_code == 400
    assert get_reviews_by_API(test_client, None, 0).status_code == 400
    assert get_reviews_by_API(test_client, None, -1).status_code == 400
    assert get_reviews_by_API(test_client, None, 'a').status_code == 400
    assert get_reviews_by_API(test_client, None, []).status_code == 400
    assert get_reviews_by_API(test_client, None, ['a']).status_code == 400
    
    # correct query parameters - user id
    correct_reviews = original_correct_reviews
    user_id = correct_reviews[0]['user_id']
    response = get_reviews_by_API(test_client, user_id)
    assert response.status_code == 200
    reviews = response.json
    correct_reviews = [p for p in correct_reviews if p['user_id'] == user_id]
    assert len(correct_reviews) == len(reviews)
    correct_reviews = sorted(correct_reviews, key=lambda k: k['comment']) 
    reviews = sorted(reviews, key=lambda k: k['comment']) 
    for idx, r in enumerate(correct_reviews):
        _check_reviews(reviews[idx], r)

    # correct query parameters - restaurant id
    correct_reviews = original_correct_reviews
    restaurant_id = correct_reviews[0]['restaurant_id']
    response = get_reviews_by_API(test_client, None, restaurant_id)
    assert response.status_code == 200
    reviews = response.json
    correct_reviews = [p for p in correct_reviews if p['restaurant_id'] == restaurant_id]
    assert len(correct_reviews) == len(reviews)
    correct_reviews = sorted(correct_reviews, key=lambda k: k['comment']) 
    reviews = sorted(reviews, key=lambda k: k['comment']) 
    for idx, r in enumerate(correct_reviews):
        _check_reviews(reviews[idx], r)

    # correct query parameters - all filters
    response = get_reviews_by_API(test_client, original_correct_reviews[0]['user_id'], original_correct_reviews[0]['restaurant_id'])
    assert response.status_code == 200
    reviews = response.json
    assert len(reviews) == 1
    _check_reviews(reviews[0], original_correct_reviews[0])