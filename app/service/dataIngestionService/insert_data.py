from app.dao.db_connections.pgsql_connection import PGSQLConnection
from config.logger_config import logger
import os

class InsertData:
    def __init__(self):
        self.pgsql_conn = None
    
    def get_pgsql_connection(self):
        try:
            self.pgsql_conn = PGSQLConnection(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", 5432),
                database=os.getenv("DB_NAME", "postgres"),
                user=os.getenv("DB_USER", "prachisingh"),
                password=os.getenv("DB_PASSWORD", "")
            )
            self.pgsql_conn.create_pool()
            return self.pgsql_conn
        except Exception as e:
            logger.error(f"Error getting PostgreSQL connection: {e}")
            raise
    
    def create_table(self, pgsql_conn):
        try:
            with pgsql_conn.get_connection() as conn:
                cursor = conn.cursor()
                create_table_query = """
                CREATE TABLE IF NOT EXISTS public.music_data (
                    index_col SERIAL UNIQUE,
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    danceability FLOAT,
                    energy FLOAT,
                    mode INT,
                    accousticness FLOAT, 
                    tempo FLOAT,
                    duration_ms INT,
                    num_sections INT,
                    num_segments INT,
                    star_rating FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                -- Create index for faster title searches
                CREATE INDEX IF NOT EXISTS idx_music_title ON music_data(title);
                """
                cursor.execute(create_table_query)
                conn.commit()
                cursor.close()
            logger.info("Table 'music_data' ensured in PostgreSQL")
        except Exception as e:
            logger.error(f"Error creating table in PostgreSQL: {e}")
            raise
    
    def insert_file_data(self, pgsql_conn, file_data):
        try:
            with pgsql_conn.get_connection() as conn:
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO music_data (id, title, danceability, energy, mode, accousticness, tempo, duration_ms, num_sections, num_segments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """
                for data in file_data:
                    cursor.execute(insert_query, (
                        data.id,
                        data.title,
                        data.danceability,
                        data.energy,
                        data.mode,
                        data.accousticness,
                        data.tempo,
                        data.duration_ms,
                        data.num_sections,
                        data.num_segments
                    ))
                conn.commit()
                cursor.close()
            logger.info("Inserted file data into PostgreSQL successfully")
        except Exception as e:
            logger.error(f"Error inserting file data into PostgreSQL: {e}")
            raise
    
    def insert_batch_data(self, pgsql_conn, file_data):
        """
        More efficient batch insert method
        """
        try:
            with pgsql_conn.get_connection() as conn:
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO music_data (id, title, danceability, energy, mode, accousticness, tempo, duration_ms, num_sections, num_segments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """
                data_tuples = [
                    (   data.id,
                        data.title,
                        data.danceability,
                        data.energy,
                        data.mode,
                        data.accousticness,
                        data.tempo,
                        data.duration_ms,
                        data.num_sections,
                        data.num_segments
                    ) for data in file_data
                ]
                cursor.executemany(insert_query, data_tuples)
                conn.commit()
                cursor.close()
            logger.info(f"Batch inserted {len(file_data)} records into PostgreSQL successfully")
        except Exception as e:
            logger.error(f"Error batch inserting file data into PostgreSQL: {e}")
            raise
    
    def close_connection(self):
        """
        Close the connection pool
        """
        if self.pgsql_conn:
            self.pgsql_conn.close_pool()