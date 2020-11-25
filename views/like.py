import connexion
from database import db_session, Restaurant, Like
from flask import request
import json
from sqlalchemy import exc


def create_like():
    request_dict = request.json

    restaurant_id = request_dict.pop('restaurant_id')
    q = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if q is None:
        return connexion.problem(404, "Not found", "There is no restaurant with the specified id")

    new_like = Like()
    new_like.user_id = request_dict.pop('user_id')
    new_like.restaurant_id = restaurant_id
    try:
        db_session.add(new_like)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return connexion.problem(403, "Forbidden", "A user cannot like the same restaurant multiple times")

    return 'Like successfully put'

