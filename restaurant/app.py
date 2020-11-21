import connexion, logging, database
from flask import jsonify


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = connexion.App(__name__, specification_dir='static/')
    app.add_api('swagger.yml')
    database.init_db()
    return app

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
app = create_app()
application = app.app

@application.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()
    

if __name__ == '__main__':
    app.run(port=5060)



'''
def task_celery():
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(
        RestaurantDeleted.reservations_service_notified == False).all()
    
    for rd in restaurants_deleted:
        response = request('microservizioReservations/reservation', 
            method='DELETE', data=dict(restaurant_id==rd.id))
        if response.status_code == 200:
            restaurants_deleted.reservations_service_notified = True
'''


'''
reservations/
reservations/{reservation_id}

reservation/restaurants/{restaurant_id}


restaurants/ 
    query: 
        - Nome
        - Cucine
        - Lat/Lon
        - working day

reservations/
    query: 
        - restaurants_id
        - user_id
        - startdate
        - enddate
'''