from flask import Flask
from flasgger import Swagger
from app.config import Config
from app.services.data_manager import DataManager
from app.utils.logger import get_logger
from app.auth import init_auth
from app.routes.areas import areas_bp
from app.routes.services import services_bp
from app.routes.web import web_bp

logger = get_logger(__name__)


def create_app(data_file: str = None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Initialize data manager
    data_manager = DataManager(data_file or Config.DATA_FILE)
    app.extensions['data_manager'] = data_manager
    
    # Initialize auth
    init_auth(app)
    
    # Initialize Swagger
    swagger = Swagger(app, template={
        "info": {
            "title": "Version Server API",
            "version": "0.2.0",
            "description": "API for managing service versions across different areas"
        },
        "securityDefinitions": {
            "basicAuth": {
                "type": "basic"
            }
        },
        "security": [
            {"basicAuth": []}
        ]
    })
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(areas_bp)
    app.register_blueprint(services_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    logger.info("Flask application created successfully")
    return app
