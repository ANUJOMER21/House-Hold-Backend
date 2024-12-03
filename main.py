from datetime import time

from celery.schedules import crontab
from flask import Flask

from CeleryTask.export_service_requests import export_service_request
from CeleryTask.send_daily_reminders import send_daily_reminders_to_customer
from SendEmail import send_email_with_attachment, send_email
from config import Config
from database import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from Routes.Admin import admin_bp
from Routes.Customer_CRUD import customer_bp
from Routes.Professional_CRUD import service_professional_bp
from Routes.Service_CRUD import service_bp
from Routes.Service_Request_CRUD import service_request_bp
from Routes.Review_CRUD import review_bp
from Routes.Professional_Routes import professional_bp
from Routes.Customer_Routes import customer_routes_bp
from Routes.Graph_Routes import analysis_blueprint
from worker import make_celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    CORS(app)
    # Initialize Celery

    with app.app_context():
        # Import models and routes here to avoid circular imports
        from models import Customer, Service, Service_Request, Review, ServiceProfessional
       # db.create_all()

        # Register blueprints







    return app

app=create_app()
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(service_professional_bp)
app.register_blueprint(service_bp)
app.register_blueprint(service_request_bp)
app.register_blueprint(review_bp)
app.register_blueprint(professional_bp)
app.register_blueprint(customer_routes_bp)
app.register_blueprint(analysis_blueprint)

celery = make_celery(app)


@celery.on_after_finalize.connect
def daily_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30, add_together.s(1, 2), name="Add Together")
    sender.add_periodic_task(crontab(hour=16, minute=00), senddailyemail.s(), name = "Daily Evening")
    #sender.add_periodic_task(30,service_export.s(),name="export_service_request")



@celery.task()
def add_together(a, b):
    time.sleep(5)
    return a + b



@celery.task()
def service_export():
    path=export_service_request()
    send_email_with_attachment(
        subject="Service request Report in CSV format",
        body="Please find the attached CSV file.",
        to_email="anujomer111@gmail.com",
        attachment_path=path
    )

@celery.task()
def senddailyemail():
    customer=send_daily_reminders_to_customer()
    for c in customer:
        send_email(
            subject="Please Check app for new offer",
            body="Please visit webiste. to get updates",
            to_email=c.customer_email
        )




if __name__ == '__main__':
    app.run(debug=True)

