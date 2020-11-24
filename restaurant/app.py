import connexion, logging
from flask import jsonify
from celery import Celery
from database import db_session, init_db, Restaurant, Like, Review, RestaurantDeleted


#TODO prendere da variabili d'ambiente
REQUEST_TIMEOUT_SECONDS = 1
RESERVATIONS_SERVICE = 'http://0.0.0.0:5010'


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = connexion.App(__name__, specification_dir='static/')
    app.add_api('swagger.yml')
    init_db()
    return app


def make_celery(app):
    celery = Celery(
        app.import_name,
        # broker=os.environ['CELERY_BROKER_URL'],
        # backend=os.environ['CELERY_BACKEND_URL']
        backend='redis://localhost:6379',
        broker='redis://localhost:6379'
    )
    celery.conf.update(app.config)
    celery.conf.beat_schedule = dict(
        hello=dict(task='app.hello',schedule=5),
        update_like_count=dict(task='app.update_like_count',schedule=30),
        update_review_count=dict(task='app.update_review_count',schedule=30),
        delete_like_and_review=dict(task='app.delete_like_and_review',schedule=30),
        delete_reservation=dict(task='app.delete_reservation',schedule=30),
        cleaner=dict(task='app.cleaner',schedule=30),
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
app = create_app()
application = app.app

celery = make_celery(application)


@application.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


@celery.task()
def hello():
    print('Celery is working!')


@celery.task
def update_like_count():
    likes = db_session.query(Like).filter(Like.marked == False).all()
    for like in likes:
        restaurant = db_session.query(Restaurant).filter_by(id=like.restaurant_id).first()
        if restaurant is not None:
            restaurant.likes += 1
        like.marked = True
        db_session.commit()


@celery.task
def update_review_count():
    reviews = db_session.query(Review).filter(Review.marked == False).all()
    for review in reviews:
        restaurant = db_session.query(Restaurant).filter_by(id=review.restaurant_id).first()
        if restaurant is not None:
            tot = restaurant.tot_reviews * restaurant.avg_rating + review.rating
            restaurant.tot_reviews += 1
            restaurant.avg_rating = tot / restaurant.tot_reviews
        review.marked = True
        db_session.commit()


@celery.task()
def delete_like_and_review():
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(
        RestaurantDeleted.likes_and_reviews_deleted == False).all()

    for restaurant in restaurants_deleted:
        likes_to_delete = db_session.query(Like).filter(Like.restaurant_id == restaurant.id).all()
        for l in likes_to_delete:
            db_session.delete(l)
        reviews_to_delete = db_session.query(Review).filter(Review.restaurant_id == restaurant.id).all()
        for r in reviews_to_delete:
            db_session.delete(r)
        restaurant.likes_and_reviews_deleted = True
        db_session.commit()


@celery.task()
def delete_reservation():
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(
        RestaurantDeleted.reservations_service_notified == False).all()

    for restaurant in restaurants_deleted:
        body = dict(restaurant_id=restaurant.id, restaurant_name=restaurant.name)
        reply = None
        try:
            reply = requests.delete(RESERVATIONS_SERVICE+'/reservations', json=body, timeout=REQUEST_TIMEOUT_SECONDS)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue
        if reply.status_code != 200:
            continue
        restaurant.reservations_service_notified = True
        db_session.commit()


@celery.task()
def cleaner():
    restaurants_deleted = db_session.query(RestaurantDeleted).filter(
        RestaurantDeleted.reservations_service_notified == True,
        RestaurantDeleted.likes_and_reviews_deleted == True
    ).all()

    for restaurant in restaurants_deleted:
        db_session.delete(restaurant)
    db_session.commit()



if __name__ == '__main__':
    app.run(port=5060)

