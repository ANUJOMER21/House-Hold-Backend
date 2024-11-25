from flask import Flask
from config import Config
from database import db  # Import the db instance
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    with app.app_context():
        # Import models here to avoid circular imports
        from models import Customer, Service, Service_Request, Review, ServiceProfessional

        db.create_all()  # Create the database schema

        # Import routes here to avoid circular imports
        from Routes.Customer_CRUD import customer_bp
        from Routes.Professional_CRUD import service_professional_bp
        from Routes.Service_CRUD import service_bp
        from Routes.Service_Request_CRUD import service_request_bp
        from Routes.Admin import admin_bp
        from Routes.Review_CRUD import review_bp
        from Routes.Professional_Routes import professional_bp
        from Routes.Customer_Routes import customer_routes_bp
        from Routes.Graph_Routes import analysis_blueprint
        # Register blueprints
        app.register_blueprint(admin_bp)
        app.register_blueprint(customer_bp)
        app.register_blueprint(service_professional_bp)
        app.register_blueprint(service_bp)
        app.register_blueprint(service_request_bp)
        app.register_blueprint(review_bp)
        app.register_blueprint(professional_bp)
        app.register_blueprint(customer_routes_bp)
        app.register_blueprint(analysis_blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
