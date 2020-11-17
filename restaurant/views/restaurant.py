
from database import Restaurant, db_session

def get_restaurants():  
    q = db_session.query(Restaurant).all()
    return [p.serialize() for p in q]

def get_restaurant(restaurant_id):  
    #TODO: Complete this :)
    q = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if q is not None:
        return q.serialize()
    else:
        return 'the specified restaurant id does not exist', 404