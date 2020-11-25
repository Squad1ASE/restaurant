from tests.conftest import test_app
from database import db_session, Restaurant, Like, Review, RestaurantDeleted
from app import update_like_count, update_review_count, delete_like_and_review, delete_reservation, cleaner
import datetime
from unittest import mock
from unittest.mock import patch


def test_update_like_count(test_app):
    app, test_client = test_app
    
    # it shouldn't do anything
    update_like_count()

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
    correct_restaurants = dict(
        owner_id = 121, name = 'Trial - 3', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).all()
    assert len(restaurant) == 3

    # create some likes
    correct_likes = [
        dict(user_id=1, restaurant_id=1),
        dict(user_id=2, restaurant_id=1),
        dict(user_id=23, restaurant_id=3)
    ]
    for idx, l in enumerate(correct_likes):
        like = Like(**l)
        db_session.add(like)
        db_session.commit()

    likes = db_session.query(Like).filter(Like.marked == True).all()
    assert len(likes) == 0
    likes = db_session.query(Like).filter(Like.marked == False).all()
    assert len(likes) == 3

    # delete a restaurant with a like
    r = db_session.query(Restaurant).filter(Restaurant.id == 3).first()
    db_session.delete(r)
    db_session.commit()

    update_like_count()

    likes = db_session.query(Like).filter(Like.marked == True).all()
    assert len(likes) == 3
    likes = db_session.query(Like).filter(Like.marked == False).all()
    assert len(likes) == 0

    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 1).first()
    assert restaurant.likes == 2
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 2).first()
    assert restaurant.likes == 0

    correct_likes = [
        dict(user_id=3, restaurant_id=2),
        dict(user_id=4, restaurant_id=1),
        dict(user_id=5, restaurant_id=2)
    ]
    for idx, l in enumerate(correct_likes):
        like = Like(**l)
        db_session.add(like)
        db_session.commit()

    update_like_count()

    likes = db_session.query(Like).filter(Like.marked == True).all()
    assert len(likes) == 6
    likes = db_session.query(Like).filter(Like.marked == False).all()
    assert len(likes) == 0

    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 1).first()
    assert restaurant.likes == 3
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 2).first()
    assert restaurant.likes == 2


def test_update_review_count(test_app):
    app, test_client = test_app
    
    now = datetime.datetime.now()

    # it shouldn't do anything
    update_review_count()

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
    correct_restaurants = dict(
        owner_id = 121, name = 'Trial - 3', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)

    db_session.commit()
    restaurant = db_session.query(Restaurant).all()
    assert len(restaurant) == 3

    # create some reviews
    correct_reviews = [
        dict(
            user_id=1, restaurant_id=1, rating=4,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=2, restaurant_id=1, rating=1,
            comment='g', date=now
        ),
        dict(
            user_id=9, restaurant_id=3, rating=1,
            comment='g', date=now
        )
    ]
    for idx, r in enumerate(correct_reviews):
        review = Review(**r)
        db_session.add(review)
        db_session.commit()

    review = db_session.query(Review).filter(Review.marked == True).all()
    assert len(review) == 0
    review = db_session.query(Review).filter(Review.marked == False).all()
    assert len(review) == 3

    # delete a restaurant with a reservation
    r = db_session.query(Restaurant).filter(Restaurant.id == 3).first()
    db_session.delete(r)
    db_session.commit()

    update_review_count()

    review = db_session.query(Review).filter(Review.marked == True).all()
    assert len(review) == 3
    review = db_session.query(Review).filter(Review.marked == False).all()
    assert len(review) == 0

    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 1).first()
    assert restaurant.tot_reviews == 2
    assert round(restaurant.avg_rating, 1) == round((1 + 4) / 2, 1)
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 2).first()
    assert restaurant.tot_reviews == 0
    assert restaurant.avg_rating == 0

    # create some reviews
    correct_reviews = [
        dict(
            user_id=3, restaurant_id=2, rating=5,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=4, restaurant_id=1, rating=5,
            comment='g', date=now
        ),
        dict(
            user_id=5, restaurant_id=2, rating=4,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=6, restaurant_id=1, rating=3,
            comment='g', date=now
        )
    ]
    for idx, r in enumerate(correct_reviews):
        review = Review(**r)
        db_session.add(review)
        db_session.commit()

    review = db_session.query(Review).filter(Review.marked == True).all()
    assert len(review) == 3
    review = db_session.query(Review).filter(Review.marked == False).all()
    assert len(review) == 4

    update_review_count()

    review = db_session.query(Review).filter(Review.marked == True).all()
    assert len(review) == 7
    review = db_session.query(Review).filter(Review.marked == False).all()
    assert len(review) == 0

    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 1).first()
    assert restaurant.tot_reviews == 4
    assert round(restaurant.avg_rating, 1)== round((1 + 4 +5 + 3) / 4, 1)
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 2).first()
    assert restaurant.tot_reviews == 2
    assert round(restaurant.avg_rating, 1)== round((5 + 4) / 2, 1)


def test_delete_like_and_review(test_app):
    app, test_client = test_app
    
    now = datetime.datetime.now()

    # it shouldn't do anything
    delete_like_and_review()

    # create 3 restaurant to test reviews
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
    correct_restaurants = dict(
        owner_id = 121, name = 'Trial - 3', lat = 22, lon = 22, phone = '3346734121', 
        cuisine_type = ['traditional'], capacity = 10, prec_measures = 'leggeX',avg_time_of_stay = 30
    )
    restaurant = Restaurant(**correct_restaurants)
    db_session.add(restaurant)
    db_session.commit()
    restaurant = db_session.query(Restaurant).all()
    assert len(restaurant) == 3

    # create some likes and reviews 
    correct_reviews = [
        dict(
            user_id=1, restaurant_id=1, rating=4,
            comment='good!', date=now, marked=False
        ),
        dict(
            user_id=2, restaurant_id=3, rating=1,
            comment='g', date=now
        ),
        dict(
            user_id=3, restaurant_id=1, rating=4,
            comment='good!', date=now, marked=False
        )
    ]
    for idx, r in enumerate(correct_reviews):
        review = Review(**r)
        db_session.add(review)
        db_session.commit()

    correct_likes = [
        dict(user_id=4, restaurant_id=2),
        dict(user_id=5, restaurant_id=3),
        dict(user_id=6, restaurant_id=2)
    ]
    for idx, l in enumerate(correct_likes):
        like = Like(**l)
        db_session.add(like)
        db_session.commit()


    # it shouldn't do anything
    delete_like_and_review()
    review = db_session.query(Review).all()
    assert len(review) == 3
    likes = db_session.query(Like).all()
    assert len(likes) == 3


    #create the delete resteurants
    correct_restaurants_deleted = [
        dict(id=1, name='Trial'),
        dict(id=3, name='Trial - 3', reservations_service_notified=True)
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()

    delete_like_and_review()

    review = db_session.query(Review).all()
    assert len(review) == 0
    likes = db_session.query(Like).all()
    assert len(likes) == 2
    review = db_session.query(Review).filter(Review.restaurant_id == 1).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 1).all()
    assert len(likes) == 0
    review = db_session.query(Review).filter(Review.restaurant_id == 2).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 2).all()
    assert len(likes) == 2
    review = db_session.query(Review).filter(Review.restaurant_id == 3).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 3).all()
    assert len(likes) == 0


    correct_restaurants_deleted = [
        dict(id=2, name='Trial'),
        dict(id=5, name='Trial not exist')
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()

    delete_like_and_review()

    review = db_session.query(Review).all()
    assert len(review) == 0
    likes = db_session.query(Like).all()
    assert len(likes) == 0
    review = db_session.query(Review).filter(Review.restaurant_id == 1).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 1).all()
    assert len(likes) == 0
    review = db_session.query(Review).filter(Review.restaurant_id == 2).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 2).all()
    assert len(likes) == 0
    review = db_session.query(Review).filter(Review.restaurant_id == 3).all()
    assert len(review) == 0
    likes = db_session.query(Like).filter(Like.restaurant_id == 3).all()
    assert len(likes) == 0


@patch('requests.delete')
def test_delete_reservation(mock1, test_app):
    app, test_client = test_app
    
    # mocked delete reservations ok
    ok_mock = mock.MagicMock()
    type(ok_mock).status_code = mock.PropertyMock(return_value=200)
    ok_mock.json.return_value = 'ok'
    mock1.return_value = ok_mock

    # it shouldn't do anything
    delete_reservation()

    #create the delete resteurants -pt1
    correct_restaurants_deleted = [
        dict(id=1, name='Trial'),
        dict(id=2, name='Trial - 2', likes_and_reviews_deleted=True)
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 0

    delete_reservation()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(
        RestaurantDeleted.reservations_service_notified == True,
        RestaurantDeleted.likes_and_reviews_deleted == True,
    ).all()
    assert len(restaurants_deleted) == 1

    #create the delete resteurants - pt2
    restaurant_deleted = RestaurantDeleted(**dict(id=3, name='Trial - 3'))
    db_session.add(restaurant_deleted)
    db_session.commit()

    # mocked delete reservations fail - 400
    not_ok_mock = mock.MagicMock()
    type(not_ok_mock).status_code = mock.PropertyMock(return_value=400)
    not_ok_mock.json.return_value = 'not ok'
    mock1.return_value = not_ok_mock

    delete_reservation()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 3
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 2

    # mocked delete reservations fail - 500
    not_ok_mock = mock.MagicMock()
    type(not_ok_mock).status_code = mock.PropertyMock(return_value=500)
    not_ok_mock.json.return_value = 'not ok'
    mock1.return_value = not_ok_mock

    delete_reservation()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 3
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 2

    # mocked delete reservations ok
    ok_mock = mock.MagicMock()
    type(ok_mock).status_code = mock.PropertyMock(return_value=200)
    ok_mock.json.return_value = 'ok'
    mock1.return_value = ok_mock

    delete_reservation()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 3
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 3


def test_delete_reservation_rais_exception(test_app):
    app, test_client = test_app

    #create the delete resteurants -pt1
    correct_restaurants_deleted = [
        dict(id=1, name='Trial'),
        dict(id=2, name='Trial - 2', likes_and_reviews_deleted=True)
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 0

    delete_reservation()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.reservations_service_notified == True).all()
    assert len(restaurants_deleted) == 0


def test_cleaner(test_app):
    app, test_client = test_app

    # it shouldn't do anything
    cleaner()

    #create the delete resteurants -pt1
    correct_restaurants_deleted = [
        dict(id=1, name='Trial', reservations_service_notified=True),
        dict(id=2, name='Trial - 2'),
        dict(id=3, name='Trial - 3', likes_and_reviews_deleted=True)
    ]
    for idx, r in enumerate(correct_restaurants_deleted):
        restaurant_deleted = RestaurantDeleted(**r)
        db_session.add(restaurant_deleted)
        db_session.commit()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 3

    cleaner()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 3

    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 2).first()
    restaurants_deleted.likes_and_reviews_deleted=True
    restaurants_deleted.reservations_service_notified=True
    db_session.commit()

    cleaner()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 2
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 1).first()
    assert restaurants_deleted is not None
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 2).first()
    assert restaurants_deleted is None
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 3).first()
    assert restaurants_deleted is not None

    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 1).first()
    restaurants_deleted.likes_and_reviews_deleted=True
    db_session.commit()
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(RestaurantDeleted.id == 3).first()
    restaurants_deleted.reservations_service_notified=True
    db_session.commit()

    cleaner()

    restaurants_deleted = db_session.query(RestaurantDeleted).all()
    assert len(restaurants_deleted) == 0