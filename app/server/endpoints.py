from flask import Blueprint, request, jsonify, g
from app.service.song_service import SongService
from config.logger_config import logger

# Create blueprint
api_bp = Blueprint('api', __name__)



@api_bp.route('/api/song/<title>', methods=['GET'])
def get_song_by_title(title: str):
    """Get all attributes of a song by title with optional pagination for partial matches"""
    logger.info(f"API: GET /api/song/{title} - Retrieving song by title")
    
    # Get pagination parameters from query string
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    
    try:
        song_service = SongService(g.db_connection)
        
        # If pagination parameters are provided, use paginated search
        if page is not None or limit is not None:
            # Set defaults for pagination
            page = page if page is not None else 1
            limit = limit if limit is not None else 10
            
            logger.info(f"API: Using paginated search for '{title}' - page: {page}, limit: {limit}")
            result = song_service.get_song_by_title_paginated(title, page, limit)
            
            if result:
                logger.info(f"API: Successfully retrieved paginated results for '{title}'")
                return jsonify({
                    "success": True,
                    "data": result
                }), 200
            else:
                logger.warning(f"API: No songs found for paginated search '{title}'")
                return jsonify({
                    "success": False,
                    "message": f"No songs found matching for paginated search '{title}'"
                }), 404
        else:
            # Original exact match behavior
            song = song_service.get_song_by_title(title)
            if song:
                logger.info(f"API: Successfully retrieved song '{title}'")
                return jsonify({
                    "success": True,
                    "data": song
                }), 200
            else:
                logger.warning(f"API: Song not found '{title}'")
                return jsonify({
                    "success": False,
                    "message": f"Song with title '{title}' not found"
                }), 404
                
    except ValueError as e:
        logger.warning(f"API: Invalid pagination parameters for '{title}': {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"API: Error retrieving song '{title}': {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/song/<title>/rate', methods=['POST'])
def rate_song(title: str):
    """Rate a song with star rating"""
    logger.info(f"API: POST /api/song/{title}/rate - Rating song")
    try:
        song_service = SongService(g.db_connection)
        
        # Handle missing or invalid JSON more gracefully
        try:
            data = request.get_json(force=True)
        except Exception:
            # If JSON parsing fails or no body provided
            logger.warning(f"API: Invalid or missing JSON in rating request for '{title}'")
            data = None
            
        if not data:
            logger.warning(f"API: Missing request body for rating '{title}'")
            return jsonify({
                "success": False,
                "message": "Request body is required"
            }), 400
        
        if 'rating' not in data:
            logger.warning(f"API: Missing rating field in request for '{title}'")
            return jsonify({
                "success": False,
                "message": "Rating is required"
            }), 400
        rating = data.get('rating')
        
        if rating is None:
            logger.warning(f"API: Rating is None for '{title}'")
            return jsonify({
                "success": False,
                "message": "Rating must be a number between 0 and 5"
            }), 400
        
        if not isinstance(rating, (int, float)) or not (0 <= rating <= 5):
            logger.warning(f"API: Invalid rating value {rating} for '{title}' - must be between 0 and 5")
            return jsonify({
                "success": False,
                "message": "Rating must be a number between 0 and 5"
            }), 400
            
        logger.debug(f"API: Attempting to rate '{title}' with {rating} stars")
        result = song_service.rate_song(title, float(rating))
        if result:
            logger.info(f"API: Successfully rated '{title}' with {rating} stars")
            return jsonify({
                "success": True,
                "data": result,
                "message": f"Successfully rated '{title}' with {rating} stars"
            }), 200
        else:
            logger.warning(f"API: Song not found for rating '{title}'")
            return jsonify({
                "success": False,
                "message": f"Song with title '{title}' not found"
            }), 404
            
    except Exception as e:
        logger.error(f"API: Error rating song '{title}': {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.debug("API: Health check endpoint accessed")
    return jsonify({
        "status": "healthy",
        "message": "Music API is running"
    }), 200