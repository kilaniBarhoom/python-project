"""
Smart Records System - Main Application
"""
from flask import Flask
from config import Config
import os

# Import blueprints
from routes import auth_bp, record_bp, comment_bp, report_bp


def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(report_bp)

    return app


if __name__ == '__main__':
    # Get environment from env variable or default to development
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app()

    print("✓ Flask application starting...")
    print("✓ Database initialized successfully!")
    print("✓ Server running at http://127.0.0.1:5000")

    app.run(debug=True)
