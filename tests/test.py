import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask
from app.server import create_app
import urllib.parse


@pytest.fixture
def mock_pool_manager():
    """Mock the pool manager to avoid database connection during tests"""
    with patch('app.server.pool_manager') as mock_pm:
        mock_pool = Mock()
        mock_pm.initialize_postgres_pool.return_value = mock_pool
        mock_pm.close_all_pools.return_value = None
        yield mock_pm, mock_pool

@pytest.fixture
def app(mock_pool_manager):
    """Create Flask app for testing with mocked database"""
    mock_pm, mock_pool = mock_pool_manager
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['DB_POOL'] = mock_pool
    
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_song_service():
    """Mock SongService for testing"""
    with patch('app.server.endpoints.SongService') as mock_service_class:
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        yield mock_service

class TestGetSongByTitleAPI:
    """Unit tests for GET /api/song/<title> endpoint"""
    
    def test_get_song_success(self, client, mock_song_service):
        """Test successful song retrieval by title"""
        mock_song_data = {
            "index_col": 1,
            "id": "5vYA1mW9g2Coh1HUFUSmlb",
            "title": "3AM",
            "danceability": 0.484,
            "energy": 0.926,
            "mode": 1,
            "accousticness": 0.0775,
            "tempo": 119.992,
            "duration_ms": 218973,
            "num_sections": 9,
            "num_segments": 370,
            "star_rating": 4.5,
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T10:30:00",
            "is_rated": True,
            "duration_minutes": 3.65
        }
        mock_song_service.get_song_by_title.return_value = mock_song_data
        
        # Make request
        response = client.get('/api/song/3AM')
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['data'] == mock_song_data
        assert data['data']['title'] == '3AM'
        assert data['data']['id'] == '5vYA1mW9g2Coh1HUFUSmlb'
        assert data['data']['star_rating'] == 4.5
        assert data['data']['is_rated'] is True
        
        # Verify service was called correctly
        mock_song_service.get_song_by_title.assert_called_once_with('3AM')
    
    def test_get_song_not_found(self, client, mock_song_service):
        """Test song not found scenario"""
        # Mock service to return None (song not found)
        mock_song_service.get_song_by_title.return_value = None
        
        # Make request
        response = client.get('/api/song/NonExistentSong')
        
        # Assertions
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert "Song with title 'NonExistentSong' not found" in data['message']
        
        # Verify service was called
        mock_song_service.get_song_by_title.assert_called_once_with('NonExistentSong')
    
    def test_get_song_with_special_characters(self, client, mock_song_service):
        """Test song title with special characters"""
        mock_song_data = {
            "title": "11:11",
            "id": "test123",
            "star_rating": None,
            "is_rated": False
        }
        mock_song_service.get_song_by_title.return_value = mock_song_data
        
        response = client.get('/api/song/11:11')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['title'] == '11:11'
        
        mock_song_service.get_song_by_title.assert_called_once_with('11:11')
    
    def test_get_song_service_exception(self, client, mock_song_service):
        """Test when service raises an exception"""
        # Mock service to raise exception
        mock_song_service.get_song_by_title.side_effect = Exception("Database connection failed")
        
        response = client.get('/api/song/3AM')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error' in data
        assert 'Database connection failed' in data['error']
    
    @pytest.mark.parametrize("song_title", [
        "3AM",
        "Song with spaces", 
        "Special!@#$%",
        "Numbers123",
        "11:11"
    ])
    def test_get_song_various_titles(self, client, mock_song_service, song_title):
        """Test various song titles"""
        mock_song_data = {"title": song_title, "id": "test"}
        mock_song_service.get_song_by_title.return_value = mock_song_data
        
        # URL encode the title for the request
        encoded_title = urllib.parse.quote(song_title, safe='')
        response = client.get(f'/api/song/{encoded_title}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['title'] == song_title
        
        # Verify service was called with decoded title
        mock_song_service.get_song_by_title.assert_called_once_with(song_title)

class TestRateSongAPI:
    """Unit tests for POST /api/song/<title>/rate endpoint"""
    
    def test_rate_song_success(self, client, mock_song_service):
        """Test successful song rating"""
        # Mock service response
        mock_rating_result = {
            "id": "5vYA1mW9g2Coh1HUFUSmlb",
            "title": "3AM",
            "rating": 4.5,
            "message": "Successfully updated rating to 4.5 stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        # Make request
        rating_data = {"rating": 4.5}
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['data'] == mock_rating_result
        assert data['message'] == "Successfully rated '3AM' with 4.5 stars"
        
        # Verify service was called correctly
        mock_song_service.rate_song.assert_called_once_with('3AM', 4.5)
    
    def test_rate_song_not_found(self, client, mock_song_service):
        """Test rating non-existent song"""
        # Mock service to return None (song not found)
        mock_song_service.rate_song.return_value = None
        
        rating_data = {"rating": 4.5}
        response = client.post(
            '/api/song/NonExistentSong/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert "Song with title 'NonExistentSong' not found" in data['message']
        
        mock_song_service.rate_song.assert_called_once_with('NonExistentSong', 4.5)
    
    def test_rate_song_missing_request_body(self, client, mock_song_service):
        """Test rating without request body"""
        response = client.post(
            '/api/song/3AM/rate',
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'Request body is required' in data['message']
        
        # Service should not be called
        mock_song_service.rate_song.assert_not_called()
    
    def test_rate_song_missing_rating_field(self, client, mock_song_service):
        """Test rating without rating field in request"""
        rating_data = {"other_field": "value"}
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'Rating is required' in data['message']
        
        mock_song_service.rate_song.assert_not_called()
    
    @pytest.mark.parametrize("invalid_rating,expected_message", [
        ("not_a_number", "Rating must be a number between 0 and 5"),
        (6, "Rating must be a number between 0 and 5"),
        (-1, "Rating must be a number between 0 and 5"),
        (5.1, "Rating must be a number between 0 and 5"),
        (-0.1, "Rating must be a number between 0 and 5"),
        ([], "Rating must be a number between 0 and 5"),
        ({}, "Rating must be a number between 0 and 5"),
        (None, "Rating must be a number between 0 and 5")
    ])
    def test_rate_song_invalid_ratings(self, client, mock_song_service, invalid_rating, expected_message):
        """Test rating with invalid rating values"""
        rating_data = {"rating": invalid_rating}
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert expected_message in data['message']
        
        mock_song_service.rate_song.assert_not_called()
    
    @pytest.mark.parametrize("valid_rating", [0, 1, 2.5, 3.0, 4.5, 5, 0.0, 5.0])
    def test_rate_song_valid_ratings(self, client, mock_song_service, valid_rating):
        """Test rating with valid rating values"""
        mock_rating_result = {
            "id": "test123",
            "title": "3AM",
            "rating": float(valid_rating),
            "message": f"Successfully updated rating to {valid_rating} stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        rating_data = {"rating": valid_rating}
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['data']['rating'] == float(valid_rating)
        
        mock_song_service.rate_song.assert_called_once_with('3AM', float(valid_rating))
    
    def test_rate_song_integer_rating(self, client, mock_song_service):
        """Test rating with integer value"""
        mock_rating_result = {
            "id": "test123",
            "title": "3AM", 
            "rating": 5.0,
            "message": "Successfully updated rating to 5.0 stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        rating_data = {"rating": 5}  # Integer
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['rating'] == 5.0
        
        # Should be converted to float
        mock_song_service.rate_song.assert_called_once_with('3AM', 5.0)
    
    def test_rate_song_service_exception(self, client, mock_song_service):
        """Test when service raises an exception"""
        mock_song_service.rate_song.side_effect = Exception("Database error")
        
        rating_data = {"rating": 4.5}
        response = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error' in data
        assert 'Database error' in data['error']
    
    def test_rate_song_invalid_json(self, client, mock_song_service):
        """Test rating with invalid JSON"""
        response = client.post(
            '/api/song/3AM/rate',
            data='invalid json data',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        mock_song_service.rate_song.assert_not_called()
    
    @pytest.mark.parametrize("song_title", [
        "3AM",
        "Song with spaces",
        "11:11",
        "Special!@#Characters"
    ])
    def test_rate_song_various_titles(self, client, mock_song_service, song_title):
        """Test rating songs with various titles"""
        mock_rating_result = {
            "id": "test123",
            "title": song_title,
            "rating": 4.0,
            "message": f"Successfully updated rating to 4.0 stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        rating_data = {"rating": 4.0}
        encoded_title = urllib.parse.quote(song_title, safe='')
        response = client.post(
            f'/api/song/{encoded_title}/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['title'] == song_title
        
        # Verify service was called with decoded title
        mock_song_service.rate_song.assert_called_once_with(song_title, 4.0)

class TestAPIWorkflow:
    """Test the workflow between both APIs"""
    
    def test_get_then_rate_workflow(self, client, mock_song_service):
        """Test getting a song and then rating it"""
        # Step 1: Get song
        mock_song_data = {
            "title": "3AM",
            "id": "test123",
            "star_rating": None,
            "is_rated": False
        }
        mock_song_service.get_song_by_title.return_value = mock_song_data
        
        response1 = client.get('/api/song/3AM')
        assert response1.status_code == 200
        
        # Step 2: Rate the same song
        mock_rating_result = {
            "id": "test123",
            "title": "3AM",
            "rating": 4.5,
            "message": "Successfully updated rating to 4.5 stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        rating_data = {"rating": 4.5}
        response2 = client.post(
            '/api/song/3AM/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['data']['rating'] == 4.5
        
        # Verify both service methods were called
        mock_song_service.get_song_by_title.assert_called_once_with('3AM')
        mock_song_service.rate_song.assert_called_once_with('3AM', 4.5)
    
    def test_rate_then_get_workflow(self, client, mock_song_service):
        """Test rating a song and then getting it"""
        # Step 1: Rate song
        mock_rating_result = {
            "id": "test123",
            "title": "TestSong",
            "rating": 3.5,
            "message": "Successfully updated rating to 3.5 stars"
        }
        mock_song_service.rate_song.return_value = mock_rating_result
        
        rating_data = {"rating": 3.5}
        response1 = client.post(
            '/api/song/TestSong/rate',
            data=json.dumps(rating_data),
            content_type='application/json'
        )
        
        assert response1.status_code == 200
        
        # Step 2: Get the same song
        mock_song_data = {
            "title": "TestSong",
            "id": "test123",
            "star_rating": 3.5,
            "is_rated": True
        }
        mock_song_service.get_song_by_title.return_value = mock_song_data
        
        response2 = client.get('/api/song/TestSong')
        assert response2.status_code == 200
        
        data2 = json.loads(response2.data)
        assert data2['data']['star_rating'] == 3.5
        assert data2['data']['is_rated'] is True
        
        # Verify both service methods were called
        mock_song_service.rate_song.assert_called_once_with('TestSong', 3.5)
        mock_song_service.get_song_by_title.assert_called_once_with('TestSong')