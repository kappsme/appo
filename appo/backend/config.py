class Config:
    """Flask configuration settings."""
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    SECRET_KEY = 'your_secret_key'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False

    # Email settings
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@example.com'
    MAIL_PASSWORD = 'your_email_password'

    # App settings
    DEBUG = True
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    
    # Other configurations can be added here