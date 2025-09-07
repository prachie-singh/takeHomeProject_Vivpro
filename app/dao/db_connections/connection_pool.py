import os
from app.dao.db_connections.pgsql_connection import PGSQLConnection
from config.logger_config import logger

class ConnectionPoolManager:
    """Manages database connection pools"""
    
    def __init__(self):
        self.pools = {}
        logger.info("ConnectionPoolManager initialized")
    
    def initialize_postgres_pool(self, pool_name='default'):
        """Initialize PostgreSQL connection pool"""
        logger.info(f"Initializing PostgreSQL connection pool: '{pool_name}'")
        try:
            pool = PGSQLConnection(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'prachisingh'),
                password=os.getenv('DB_PASSWORD', ''),
                minconn=int(os.getenv('DB_MIN_CONN', 2)),
                maxconn=int(os.getenv('DB_MAX_CONN', 10))
            )
            pool.create_pool()
            self.pools[pool_name] = pool
            logger.info(f"PostgreSQL connection pool '{pool_name}' initialized successfully")
            return pool
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool '{pool_name}': {e}")
            raise
    
    def get_pool(self, pool_name='default'):
        """Get a connection pool by name"""
        logger.debug(f"Retrieving connection pool: '{pool_name}'")
        pool = self.pools.get(pool_name)
        if pool:
            logger.debug(f"Connection pool '{pool_name}' found and returned")
        else:
            logger.warning(f"Connection pool '{pool_name}' not found")
        return pool
    
    def close_all_pools(self):
        """Close all connection pools"""
        logger.info(f"Closing all connection pools. Total pools: {len(self.pools)}")
        for pool_name, pool in self.pools.items():
            try:
                pool.close_pool()
                logger.info(f"Connection pool '{pool_name}' closed successfully")
            except Exception as e:
                logger.error(f"Error closing pool '{pool_name}': {e}")
        self.pools.clear()
        logger.info("All connection pools cleared")

# Global instance
pool_manager = ConnectionPoolManager()