import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///transitops.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secure SECRET_KEY config: fail loudly in non-development envs if not set
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if os.environ.get("FLASK_ENV") == "production":
            raise ValueError("SECRET_KEY environment variable is not defined in production environment!")
        SECRET_KEY = "dev-fallback-secret-key-do-not-use-in-prod"