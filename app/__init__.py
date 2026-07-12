from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import engine, SessionLocal
from app.models import Base

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend Vite dev server (default 5173 / local)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Create tables if SQLite database doesn't exist
    Base.metadata.create_all(bind=engine)

    # Teardown database session context on request end
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    # Import and register routes blueprints
    from app.routes.auth import auth_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.drivers import drivers_bp
    from app.routes.trips import trips_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.operations import operations_bp
    from app.routes.web import web_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicles_bp, url_prefix='/api/vehicles')
    app.register_blueprint(drivers_bp, url_prefix='/api/drivers')
    app.register_blueprint(trips_bp, url_prefix='/api/trips')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(operations_bp, url_prefix='/api/operations')
    app.register_blueprint(web_bp, url_prefix='/api')


    return app
