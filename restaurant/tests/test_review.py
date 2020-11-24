from tests.conftest import test_app
from database import db_session, Restaurant, Review
from sqlalchemy import exc
from tests.utilities import get_reviews_by_API
import datetime


def _check_reviews(review_obj, dict_review):
    review = review_obj.serialize()
    for key in dict_review.keys():
        if key == 'date':
            assert review['date'] == dict_review['date'].strftime("%d/%m/%Y")
        elif key == 'marked':
            assert review_obj.marked == dict_review['marked']
        else:
            assert review[key] == dict_review[key]
    if 'marked' not in dict_review:
        assert review_obj.marked == False


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


def test_create_review(test_app):
    app, test_client = test_app

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


    #TODO: SIMULARE MOCK


    # check total reviews
    reviews = db_session.query(Review).all()
    assert len(reviews) == 2


def aaa_test_get_reviews(test_app):
    app, test_client = test_app
    
    # empty get 
    response = get_reviews_by_API(test_client)
    assert response.status_code == 200
    assert response.json == []
    
    # create some restaurants
    correct_restaurants = restaurant_examples
    for idx, r in enumerate(correct_restaurants):
        assert create_restaurant_by_API(test_client, r).status_code == 200
    
    # correct get 
    response = get_reviews_by_API(test_client)
    assert response.status_code == 200
    restaurants = response.json
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # bad query parameters
    assert get_reviews_by_API(test_client, 0).status_code == 400
    assert get_reviews_by_API(test_client, -1).status_code == 400
    assert get_reviews_by_API(test_client, 'a').status_code == 400
    assert get_reviews_by_API(test_client, []).status_code == 400
    assert get_reviews_by_API(test_client, ['a']).status_code == 400
    assert get_reviews_by_API(test_client, None, None, 1).status_code == 400
    assert get_reviews_by_API(test_client, None, None, 'a').status_code == 400
    assert get_reviews_by_API(test_client, None, None, []).status_code == 400
    assert get_reviews_by_API(test_client, None, None, ['a']).status_code == 400
    assert get_reviews_by_API(test_client, None, None, None, 1).status_code == 400
    assert get_reviews_by_API(test_client, None, None, None, 'a').status_code == 400
    assert get_reviews_by_API(test_client, None, None, None, []).status_code == 400
    assert get_reviews_by_API(test_client, None, None, None, ['a']).status_code == 400
    assert get_reviews_by_API(test_client, None, None, 1, 'a').status_code == 400
    assert get_reviews_by_API(test_client, None, None, 'a', 1).status_code == 400
    
    # correct query parameters - owner id
    correct_restaurants = restaurant_examples
    owner_id = correct_restaurants[0]['owner_id']
    response = get_reviews_by_API(test_client, owner_id)
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
    response = get_reviews_by_API(test_client, None, '-')
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
    response = get_reviews_by_API(test_client, None, None, restaurant_examples[0]['lat'], restaurant_examples[0]['lon'])
    assert response.status_code == 200
    restaurants = response.json
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)

    # correct query parameters - cuisine type
    correct_restaurants = restaurant_examples
    response = get_reviews_by_API(test_client, None, None, None, None, ['italian', 'pizzeria'])
    assert response.status_code == 200
    restaurants = response.json
    correct_restaurants = [p for p in correct_restaurants if any(i in p['cuisine_type'] for i in ['italian', 'pizzeria'])]
    assert len(correct_restaurants) == len(restaurants)
    correct_restaurants = sorted(correct_restaurants, key=lambda k: k['name']) 
    restaurants = sorted(restaurants, key=lambda k: k['name']) 
    for idx, r in enumerate(correct_restaurants):
        _check_restaurants(restaurants[idx], r)


    # correct query parameters - all filters
    response = get_reviews_by_API(
        test_client, restaurant_examples[0]['owner_id'], restaurant_examples[0]['name'], 
        restaurant_examples[0]['lat'], restaurant_examples[0]['lon'], ['italian', 'pizzeria']
    )
    assert response.status_code == 200
    restaurants = response.json
    assert len(restaurants) == 1
    _check_restaurants(restaurants[0], restaurant_examples[0])
