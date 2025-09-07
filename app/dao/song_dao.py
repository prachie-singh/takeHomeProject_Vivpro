from typing import Optional, Dict, List, Tuple
from config.logger_config import logger

class SongDAO:
    """Data Access Object for song-related database operations"""
    
    def __init__(self, db_connection=None):
        """
        Initialize SongDAO with database connection
        
        Args:
            db_connection: Database connection pool instance
        """
        self.db_connection = db_connection
        logger.info("SongDAO initialized")

    def check_song_exists(self, title: str) -> bool:
        """
        Check if a song exists by title
        
        Args:
            title (str): Song title to check
            
        Returns:
            bool: True if song exists, False otherwise
            
        Raises:
            Exception: If database connection fails or query fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.check_song_exists")
            raise Exception("Database connection not initialized")
        
        logger.debug(f"DAO: Checking if song exists: '{title}'")
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 1 FROM music_data 
                    WHERE title = %s
                    LIMIT 1;
                """
                cursor.execute(query, (title,))
                result = cursor.fetchone()
                cursor.close()
                logger.debug(f"DAO: Song exists check result for '{title}': {result is not None}")
                return result is not None
                
        except Exception as e:
            logger.error(f"DAO Error checking if song exists '{title}': {e}")
            raise
    
    def get_song_by_title(self, title: str) -> Optional[Tuple]:
        """
        Get song data by title from database
        
        Args:
            title (str): Song title to search for
            
        Returns:
            Optional[Tuple]: Raw database row if found, None otherwise
            
        Raises:
            Exception: If database connection fails or query fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.get_song_by_title")
            raise Exception("Database connection not initialized")

        logger.debug(f"DAO: Querying database for song title: '{title}'")
        
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT index_col, id, title, danceability, energy, mode, 
                           accousticness, tempo, duration_ms, num_sections, 
                           num_segments, star_rating, created_at, updated_at
                    FROM music_data 
                    WHERE LOWER(title) = LOWER(%s);
                """
                cursor.execute(query, (title,))
                result = cursor.fetchone()
                cursor.close()
                if result:
                    logger.debug(f"DAO: Song found in database: '{title}' (ID: {result[1]})")
                else:
                    logger.debug(f"DAO: Song not found in database: '{title}'")
                return result
                
        except Exception as e:
            logger.error(f"DAO Error getting song by title '{title}': {e}")
            raise
    
    def update_song_rating(self, title: str, rating: float) -> Optional[Tuple]:
        """
        Update star rating for a song by title
        
        Args:
            title (str): Song title to update
            rating (float): New rating value
            
        Returns:
            Optional[Tuple]: Updated song data (id, title, rating) if successful
            
        Raises:
            Exception: If database connection fails or update fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.update_song_rating")
            raise Exception("Database connection not initialized")

        logger.debug(f"DAO: Updating song rating - Title: '{title}', Rating: {rating}")
        
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                update_query = """
                    UPDATE music_data 
                    SET star_rating = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE LOWER(title) = LOWER(%s)
                    RETURNING id, title, star_rating;
                """
                cursor.execute(update_query, (rating, title))
                result = cursor.fetchone()
                conn.commit()
                cursor.close()
                if result:
                    logger.info(f"DAO: Successfully updated rating for '{title}' to {rating} stars (ID: {result[0]})")
                else:
                    logger.warning(f"DAO: No song found to update rating for '{title}'")
                return result
                
        except Exception as e:
            logger.error(f"DAO Error updating song rating for '{title}': {e}")
            raise
        
    def get_songs_paginated(self, limit: int, offset: int) -> List[Tuple]:
        """
        Get songs with pagination
        
        Args:
            limit (int): Number of songs to return
            offset (int): Number of songs to skip
            
        Returns:
            List[Tuple]: List of song tuples
            
        Raises:
            Exception: If database connection fails or query fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.get_songs_paginated")
            raise Exception("Database connection not initialized")

        logger.debug(f"DAO: Getting paginated songs - Limit: {limit}, Offset: {offset}")
        
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT title, id, star_rating, danceability, energy, mode
                    FROM music_data 
                    ORDER BY title 
                    LIMIT %s OFFSET %s;
                """
                cursor.execute(query, (limit, offset))
                results = cursor.fetchall()
                cursor.close()
                logger.info(f"DAO: Retrieved {len(results)} songs with pagination")
                return results
                
        except Exception as e:
            logger.error(f"DAO Error getting paginated songs: {e}")
            raise
    

    def get_songs_by_title_paginated(self, title: str, limit: int, offset: int) -> List[Tuple]:
        """
        Get songs by title with pagination (supports partial matching)
        
        Args:
            title (str): Title to search for (partial match)
            limit (int): Number of songs to return
            offset (int): Number of songs to skip
            
        Returns:
            List[Tuple]: List of matching song tuples
            
        Raises:
            Exception: If database connection fails or query fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.get_songs_by_title_paginated")
            raise Exception("Database connection not initialized")

        logger.debug(f"DAO: Getting songs by title with pagination - Title: '{title}', Limit: {limit}, Offset: {offset}")
        
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT id, title, star_rating, danceability, energy, mode, 
                        accousticness, tempo, duration_ms
                    FROM music_data 
                    WHERE LOWER(title) LIKE LOWER(%s)
                    ORDER BY 
                        CASE WHEN LOWER(title) = LOWER(%s) THEN 0 ELSE 1 END,
                        title
                    LIMIT %s OFFSET %s;
                """
                search_term = f"%{title}%"
                cursor.execute(query, (search_term, title, limit, offset))
                results = cursor.fetchall()
                cursor.close()
                
                logger.info(f"DAO: Retrieved {len(results)} songs matching '{title}' with pagination")
                return results
                
        except Exception as e:
            logger.error(f"DAO Error getting paginated songs by title '{title}': {e}")
            raise

    def get_songs_count_by_title(self, title: str) -> int:
        """
        Get count of songs matching title search
        
        Args:
            title (str): Title to search for (partial match)
            
        Returns:
            int: Number of matching songs
            
        Raises:
            Exception: If database connection fails or query fails
        """
        if not self.db_connection:
            logger.error("Database connection not initialized in SongDAO.get_songs_count_by_title")
            raise Exception("Database connection not initialized")

        logger.debug(f"DAO: Getting count of songs matching title '{title}'")
        
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT COUNT(*) 
                    FROM music_data 
                    WHERE LOWER(title) LIKE LOWER(%s);
                """
                search_term = f"%{title}%"
                cursor.execute(query, (search_term,))
                result = cursor.fetchone()
                cursor.close()
                
                count = result[0] if result else 0
                logger.debug(f"DAO: Found {count} songs matching '{title}'")
                return count
                
        except Exception as e:
            logger.error(f"DAO Error getting count for songs matching title '{title}': {e}")
            raise