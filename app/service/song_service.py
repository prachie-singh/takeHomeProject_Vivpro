from typing import Optional, Dict, List, Tuple
from app.dao.song_dao import SongDAO
from config.logger_config import logger

class SongService:
    """Service class for handling song-related business logic"""
    
    def __init__(self, db_connection=None):
        """
        Initialize SongService with database connection
        
        Args:
            db_connection: Database connection pool instance
        """
        self.song_dao = SongDAO(db_connection)
        logger.info("SongService initialized")
    
    def get_song_by_title(self, title: str) -> Optional[Dict]:
        """
        Get all attributes of a song by title with business logic processing
        
        Args:
            title (str): Song title to search for
            
        Returns:
            Optional[Dict]: Processed song data if found, None otherwise
            
        Raises:
            ValueError: If title is empty or invalid
            Exception: If database operation fails
        """
        logger.info(f"Service: Getting song by title '{title}'")
        
        # Pre-processing: Validate input
        if not title or not title.strip():
            logger.error("Service: Song title is empty or None")
            raise ValueError("Song title cannot be empty")
        
        if len(title) > 255:
            logger.error(f"Service: Song title too long: {len(title)} characters")
            raise ValueError("Song title too long (maximum 255 characters)")
        if '\x00' in title:  # Null byte check
            logger.error("Service: Song title contains null bytes")
            raise ValueError("Song title contains invalid characters")
        
        title = title.strip()
        logger.debug(f"Service: Processed title: '{title}'")
        
        try:
            # Call DAO layer
            song_data = self.song_dao.get_song_by_title(title)
            
            if not song_data:
                logger.info(f"Service: Song not found '{title}'")
                return None
            
            # Post-processing: Convert tuple to structured dictionary
            result = self._format_full_song_data(song_data)
            logger.info(f"Service: Successfully retrieved and formatted song '{title}' (ID: {result.get('id')})")
            return result
            
        except Exception as e:
            logger.error(f"Service Error getting song by title '{title}': {e}")
            raise
    def get_song_by_title_paginated(self, title: str, page: int = 1, limit: int = 10) -> Optional[Dict]:
        """
        Get songs by title with pagination (supports partial matching)
        
        Args:
            title (str): Song title to search for (partial match)
            page (int): Page number (1-based)
            limit (int): Number of songs per page
            
        Returns:
            Optional[Dict]: Paginated song data with metadata if found, None otherwise
            
        Raises:
            ValueError: If title is empty or pagination parameters are invalid
            Exception: If database operation fails
        """
        logger.info(f"Service: Getting songs by title with pagination - title: '{title}', page: {page}, limit: {limit}")
        
        # Pre-processing: Validate input
        if not title or not title.strip():
            logger.error("Service: Song title is empty or None for paginated search")
            raise ValueError("Song title cannot be empty")
        
        if len(title) > 255:
            logger.error(f"Service: Song title too long for paginated search: {len(title)} characters")
            raise ValueError("Song title too long (maximum 255 characters)")
        
        # Validate pagination parameters
        if page < 1:
            logger.error(f"Service: Invalid page number {page} - must be >= 1")
            raise ValueError("Page number must be >= 1")
        
        if limit < 1 or limit > 100:
            logger.error(f"Service: Invalid limit {limit} - must be between 1 and 100")
            raise ValueError("Limit must be between 1 and 100")
        
        title = title.strip()
        logger.debug(f"Service: Processed title for paginated search: '{title}'")
        
        try:
            # Calculate offset
            offset = (page - 1) * limit
            logger.debug(f"Service: Calculated offset for pagination: {offset}")
            
            # Get paginated songs and total count
            songs_data = self.song_dao.get_songs_by_title_paginated(title, limit, offset)
            total_count = self.song_dao.get_songs_count_by_title(title)
            
            if not songs_data:
                logger.info(f"Service: No songs found for paginated search: '{title}'")
                return None
            
            # Calculate pagination metadata
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
            
            # Format songs data
            formatted_songs = []
            for song_tuple in songs_data:
                formatted_song = self._format_paginated_song_data(song_tuple)
                formatted_songs.append(formatted_song)
            
            result = {
                "songs": formatted_songs,
                "search_term": title,
                "pagination": {
                    "current_page": page,
                    "per_page": limit,
                    "total_results": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "next_page": page + 1 if has_next else None,
                    "prev_page": page - 1 if has_prev else None
                }
            }
            
            logger.info(f"Service: Successfully retrieved {len(formatted_songs)} songs for '{title}' (page {page}/{total_pages})")
            return result
            
        except Exception as e:
            logger.error(f"Service: Error getting paginated songs by title '{title}': {e}")
            raise

    def _format_paginated_song_data(self, song_tuple: Tuple) -> Dict:
        """
        Format song tuple for paginated results
        
        Args:
            song_tuple: Raw database tuple from paginated query
            
        Returns:
            Dict: Formatted song data for pagination
        """
        logger.debug("Service: Formatting paginated song data")
        return {
            "id": song_tuple[0],
            "title": song_tuple[1], 
            "star_rating": song_tuple[2],
            "danceability": song_tuple[3],
            "energy": song_tuple[4],
            "mode": song_tuple[5],
            "accousticness": song_tuple[6],
            "tempo": song_tuple[7],
            "duration_ms": song_tuple[8],
            "is_rated": song_tuple[2] is not None
        }
    def rate_song(self, title: str, rating: float) -> Optional[Dict]:
        """
        Rate a song with validation and business logic
        
        Args:
            title (str): Song title to rate
            rating (float): Rating value between 0 and 5
            
        Returns:
            Optional[Dict]: Updated song data if successful, None if song not found
            
        Raises:
            ValueError: If title is empty or rating is invalid
            Exception: If database operation fails
        """
        logger.info(f"Service: Rating song '{title}' with {rating} stars")
        
        # Pre-processing: Validate inputs
        if not title or not title.strip():
            logger.error("Service: Song title is empty for rating")
            raise ValueError("Song title cannot be empty")
        
        if not isinstance(rating, (int, float)):
            logger.error(f"Service: Invalid rating type {type(rating)} for '{title}'")
            raise ValueError("Rating must be a number")
        
        if not (0 <= rating <= 5):
            logger.error(f"Service: Rating {rating} out of range for '{title}'")
            raise ValueError("Rating must be between 0 and 5")
        
        title = title.strip()
        rating = round(float(rating), 1)  # Round to 1 decimal place
        logger.debug(f"Service: Processed rating request - Title: '{title}', Rating: {rating}")
        
        try:
            # Check if song exists first
            logger.debug(f"Service: Checking if song exists '{title}'")
            if not self.song_dao.check_song_exists(title):
                logger.warning(f"Service: Song not found for rating '{title}'")
                return None
            
            # Call DAO layer to update rating
            updated_data = self.song_dao.update_song_rating(title, rating)
            
            if not updated_data:
                logger.warning(f"Service: Failed to update rating for '{title}'")
                return None
            
            # Post-processing: Format response
            result = {
                "id": updated_data[0],
                "title": updated_data[1],
                "rating": updated_data[2],
                "message": f"Successfully updated rating to {rating} stars"
            }
            logger.info(f"Service: Successfully rated '{title}' with {rating} stars (ID: {result['id']})")
            return result
            
        except Exception as e:
            logger.error(f"Service Error rating song '{title}': {e}")
            raise
    
    def get_all_songs(self, page: int = 1, limit: int = 20) -> Dict:
        """
        Get all songs with pagination and metadata
        
        Args:
            page (int): Page number (1-based)
            limit (int): Number of songs per page
            
        Returns:
            Dict: Paginated results with metadata
            
        Raises:
            ValueError: If pagination parameters are invalid
            Exception: If database operation fails
        """
        logger.info(f"Service: Getting all songs - Page: {page}, Limit: {limit}")
        
        # Pre-processing: Validate pagination parameters
        if page < 1:
            logger.error(f"Service: Invalid page number {page}")
            raise ValueError("Page number must be 1 or greater")
        
        if limit < 1 or limit > 100:
            logger.error(f"Service: Invalid limit {limit}")
            raise ValueError("Limit must be between 1 and 100")
        
        try:
            offset = (page - 1) * limit
            logger.debug(f"Service: Calculated offset: {offset}")
            
            # Call DAO layer
            results = self.song_dao.get_songs_paginated(limit, offset)
            
            # Post-processing: Format results with metadata
            songs = []
            for row in results:
                song_data = {
                    "title": row[0],
                    "id": row[1],
                    "rating": row[2],
                    "danceability": round(row[3], 3) if row[3] else None,
                    "energy": round(row[4], 3) if row[4] else None,
                    "mode": row[5],
                    "is_rated": row[2] is not None
                }
                songs.append(song_data)
            
            result = {
                "songs": songs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "count": len(songs),
                    "has_more": len(songs) == limit
                }
            }
            
            logger.info(f"Service: Successfully retrieved {len(songs)} songs for page {page}")
            return result
            
        except Exception as e:
            logger.error(f"Service Error getting all songs: {e}")
            raise
    
    def _format_full_song_data(self, song_tuple: tuple) -> Dict:
        """
        Helper method to format full song data from database tuple
        
        Args:
            song_tuple: Raw database tuple
            
        Returns:
            Dict: Formatted song data
        """
        logger.debug("Service: Formatting full song data from database tuple")
        column_names = [
            'index_col', 'id', 'title', 'danceability', 'energy', 
            'mode', 'accousticness', 'tempo', 'duration_ms', 
            'num_sections', 'num_segments', 'star_rating', 
            'created_at', 'updated_at'
        ]
        
        song_dict = dict(zip(column_names, song_tuple))
        
        # Add computed fields
        song_dict['is_rated'] = song_dict['star_rating'] is not None
        song_dict['duration_minutes'] = round(song_dict['duration_ms'] / 60000, 2) if song_dict['duration_ms'] else None
        
        # Round float values for better presentation
        float_fields = ['danceability', 'energy', 'accousticness', 'tempo']
        for field in float_fields:
            if song_dict[field] is not None:
                song_dict[field] = round(song_dict[field], 3)
        
        logger.debug(f"Service: Formatted song data for '{song_dict.get('title')}' with {len(song_dict)} fields")
        return song_dict