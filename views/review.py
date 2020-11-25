import connexion
from database import db_session, Restaurant, Review
from flask import request
from sqlalchemy import or_, and_
import json
import datetime
import requests
import os


#TODO prendere da variabili d'ambiente
REQUEST_TIMEOUT_SECONDS = 1
#RESERVATIONS_SERVICE = 'http://0.0.0.0:5010'
RESERVATIONS_SERVICE = os.environ['RESERVATION_SERVICE']


def _compose_url_get_reservations(user_id, restaurant_id, end):
    end_date = end.isoformat()
    url = RESERVATIONS_SERVICE + '/reservations'
    url += '?user_id=' + str(user_id) + '&restaurant_id=' + str(restaurant_id) + '&end=' + str(end_date)
    return url


def create_review():
    request_dict = request.json

    user_id = request_dict.pop('user_id')
    restaurant_id = request_dict.pop('restaurant_id')
    now = datetime.datetime.now()

    q = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if q is None:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")

    # to make a review it is necessary that the user has made a reservation in the past in that restaurant
    reply = None
    try:
        url = _compose_url_get_reservations(user_id=user_id, restaurant_id=restaurant_id, end=now)
        reply = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return connexion.problem(500, "Internal server error", "Reservations service not available")
    if reply.status_code != 200:
        return connexion.problem(500, "Internal server error", "Reservations service not available")

    # if the user has never been to that restaurant
    reply_json = reply.json()
    if len(reply_json) == 0:
        return connexion.problem(403, "Forbidden", "The user must have made a reservation to make a review")

    new_review = Review()
    new_review.user_id = user_id
    new_review.restaurant_id = restaurant_id
    new_review.comment = request_dict.pop('comment')
    new_review.rating = request_dict.pop('rating')
    new_review.date = now
    try:
        db_session.add(new_review)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return connexion.problem(403, "Forbidden", "A user cannot review the same restaurant multiple times")

    return 'Review successfully made'


def get_reviews():
    user_id = request.args['user_id'] if 'user_id' in request.args else None
    restaurant_id = request.args['restaurant_id'] if 'restaurant_id' in request.args else None

    q = db_session.query(Review)
    
    if user_id is not None:
        q = q.filter(Review.user_id == user_id)
    
    if restaurant_id is not None:
        q = q.filter(Review.restaurant_id == restaurant_id)

    reviews = q.all()
    return [p.serialize() for p in reviews]

