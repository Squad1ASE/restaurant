from tests.conftest import test_app
from database import db_session, Restaurant, Like
from sqlalchemy import exc


def _check_likes(like, dict_like):
    like = like.serialize()
    for key in dict_like.keys():
        assert like[key] == dict_like[key]
    if 'marked' not in dict_like:
        assert like['marked'] == False


def test_insertDB_like(test_app):
    app, test_client = test_app

    # create a restaurant to test likes
    correct_restaurants = dict(
        owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()

    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # incorrect likes pt1 - fail check validators
    incorrect_likes = [
        dict(user_id=None, restaurant_id=restaurant.id, marked=False),
        dict(user_id=0, restaurant_id=restaurant.id, marked=False),
        dict(user_id=-1, restaurant_id=restaurant.id, marked=False),
        dict(user_id='a', restaurant_id=restaurant.id, marked=False),
        dict(user_id=[], restaurant_id=restaurant.id, marked=False),
        dict(user_id=['a'], restaurant_id=restaurant.id, marked=False),
        dict(user_id=1, restaurant_id=None, marked=False),
        dict(user_id=1, restaurant_id=0, marked=False),
        dict(user_id=1, restaurant_id=-1, marked=False),
        dict(user_id=1, restaurant_id='a', marked=False),
        dict(user_id=1, restaurant_id=[], marked=False),
        dict(user_id=1, restaurant_id=['a'], marked=False),
        dict(user_id=1, restaurant_id=restaurant.id, marked=1),
        dict(user_id=1, restaurant_id=restaurant.id, marked='a'),
        dict(user_id=1, restaurant_id=restaurant.id, marked=[]),
        dict(user_id=1, restaurant_id=restaurant.id, marked=['a'])
    ]
    count_assert = 0
    for l in incorrect_likes:
        try:
            like = Like(**l)
        except ValueError:
            count_assert += 1
            assert True
    assert len(incorrect_likes) == count_assert
    

    # incorrect likes pt2 - missing mandatory fields
    incorrect_likes = [
        dict(restaurant_id=restaurant.id, marked=False),
        dict(user_id=1, marked=False)
    ]
    count_assert = 0
    for l in incorrect_likes:
        like = Like(**l)
        try:
            db_session.add(like)
            db_session.commit()
        except (exc.IntegrityError, exc.InvalidRequestError):
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_likes) == count_assert

    # correct likes
    correct_likes = [
        dict(user_id=1, restaurant_id=restaurant.id, marked=False),
        dict(user_id=2, restaurant_id=restaurant.id)
    ]
    for idx, l in enumerate(correct_likes):
        like = Like(**l)
        db_session.add(like)
        db_session.commit()
        like_to_check = db_session.query(Like).filter(Like.user_id == correct_likes[idx]['user_id']).first()
        assert like_to_check is not None
        _check_likes(like_to_check, correct_likes[idx])

    # incorrect likes pt3 - a user cannot like the same restaurant multiple times
    incorrect_likes = [
        dict(user_id=1, restaurant_id=restaurant.id, marked=False),
        dict(user_id=2, restaurant_id=restaurant.id)
    ]
    count_assert = 0
    for l in incorrect_likes:
        like = Like(**l)
        try:
            db_session.add(like)
            db_session.commit()
        except Exception:
            db_session.rollback()
            count_assert += 1
            assert True
    assert len(incorrect_likes) == count_assert

    # check total likes
    likes = db_session.query(Like).all()
    assert len(likes) == len(correct_likes)


def test_create_like(test_app):
    app, test_client = test_app

    # incorrect create like - restaurant_id not exists
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=1), follow_redirects=True).status_code == 404
    
    # create a restaurant to test likes
    correct_restaurants = dict(
        owner_id = 1, name = 'Trial', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()

    restaurant = db_session.query(Restaurant).first()
    assert restaurant is not None

    # bad query parameters
    assert test_client.put('/likes', json=dict(restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=None, restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=0, restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=-1, restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id='a', restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=[], restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=['a'], restaurant_id=restaurant.id), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=0), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=-1), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id='a'), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=[]), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=['a']), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=None), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(user_id=1, trial='hello'), follow_redirects=True).status_code == 400
    assert test_client.put('/likes', json=dict(trial='hello', restaurant_id=restaurant.id), follow_redirects=True).status_code == 400

    # correct create like pt1
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=restaurant.id), follow_redirects=True).status_code == 200
    like_to_check = db_session.query(Like).filter(Like.user_id == 1).first()
    assert like_to_check is not None
    _check_likes(like_to_check, dict(user_id=1, restaurant_id=restaurant.id))

    # correct create like pt2
    assert test_client.put('/likes', json=dict(user_id=2, restaurant_id=restaurant.id, trial='hello'), follow_redirects=True).status_code == 200
    like_to_check = db_session.query(Like).filter(Like.user_id == 2).first()
    assert like_to_check is not None
    _check_likes(like_to_check, dict(user_id=2, restaurant_id=restaurant.id))

    # attempt to put like with the same user
    assert test_client.put('/likes', json=dict(user_id=1, restaurant_id=restaurant.id), follow_redirects=True).status_code == 403

    # check total likes
    likes = db_session.query(Like).all()
    assert len(likes) == 2