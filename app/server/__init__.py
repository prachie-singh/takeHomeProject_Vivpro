from flask import Flask, g, current_app
import atexit
from app.dao.db_connections.connection_pool import pool_manager
from config.logger_config import logger

def create_app():
    """Create Flask app with database connection"""
    logger.info("Creating Flask application")
    app = Flask(__name__)
    
    # Initialize database connection pool
    logger.info("Initializing database connection pool for Flask app")
    with app.app_context():
        db_pool = pool_manager.initialize_postgres_pool('main_pool')
        app.config['DB_POOL'] = db_pool
        logger.info("Database connection pool configured in Flask app")
    
    @app.before_request
    def before_request():
        """Store database connection in Flask g for each request"""
        logger.debug("Setting up database connection for request")
        g.db_connection = current_app.config['DB_POOL']
    
    # Register cleanup function
    @atexit.register
    def cleanup_pools():
        """Cleanup database connection pools on application shutdown"""
        logger.info("Application shutdown - cleaning up database connection pools")
        pool_manager.close_all_pools()
        logger.info("All database connection pools closed")
    
    # Register blueprints
    logger.info("Registering API blueprints")
    from app.server.endpoints import api_bp
    app.register_blueprint(api_bp)
    logger.info("Flask application created successfully")
    
    return app