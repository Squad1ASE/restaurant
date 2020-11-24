import connexion
from database import db_session, Restaurant, Review
from flask import request
from sqlalchemy import or_, and_
import json
import datetime


def create_review():
    request_dict = request.json
    
    user_id = request_dict.pop('user_id')
    restaurant_id = request_dict.pop('restaurant_id')

    q = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if q is None:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")


    #TODO:chiamata a reservations


    new_review = Review()
    new_review.user_id = user_id
    new_review.restaurant_id = restaurant_id
    new_review.comment = request_dict.pop('comment')
    new_review.rating = request_dict.pop('rating')
    new_review.date = datetime.datetime.now()
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

