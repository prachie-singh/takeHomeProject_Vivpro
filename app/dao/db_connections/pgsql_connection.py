import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config.logger_config import logger

class PGSQLConnection:
    """
    A class to manage PostgreSQL database connections with connection pooling
    """
    def __init__(self, host: str, port: int, database: str, user: str, password: str, 
                 minconn: int = 1, maxconn: int = 10):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection_pool = None
        self.minconn = minconn
        self.maxconn = maxconn
        logger.info(f"PGSQLConnection initialized - Host: {host}, Port: {port}, Database: {database}, User: {user}, Pool size: {minconn}-{maxconn}")
        
    def create_pool(self):
        """
        Create a connection pool
        """
        logger.debug(f"Creating PostgreSQL connection pool - Min: {self.minconn}, Max: {self.maxconn}")
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.minconn,
                self.maxconn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info("PostgreSQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool using context manager
        """
        connection = None
        logger.debug("Attempting to get connection from pool")
        try:
            connection = self.connection_pool.getconn()
            logger.debug("Connection acquired from pool successfully")
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
                logger.warning("Database transaction rolled back due to error")
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
                logger.debug("Connection returned to pool")
    
    def close_pool(self):
        """
        Close all connections in the pool
        """
        logger.info("Closing PostgreSQL connection pool")
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("PostgreSQL connection pool closed successfully")
        else:
            logger.warning("No connection pool to close")