class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin_password'  # Store hashed passwords in production
    JWT_SECRET_KEY = 'your_jwt_secret_key'
