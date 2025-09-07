# Music API - Take Home Project

A Flask-based REST API for managing and rating songs with PostgreSQL database backend.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Logging](#logging)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Features

- **Song Management**: Retrieve song information by title
- **Rating System**: Rate songs with 0-5 star ratings
- **Database Integration**: PostgreSQL with connection pooling
- **Comprehensive Logging**: Structured logging across all layers
- **Data Ingestion**: Service for importing song data from a JSON file
- **Health Monitoring**: Health check endpoint
- **Input Validation**: Robust validation and error handling
- **Exception Handling**: Proper error responses with meaningful messages

## Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: PostgreSQL
- **Testing**: pytest
- **Logging**: Python logging with custom configuration
- **Environment**: python-dotenv for configuration management
- **Data Processing**: pandas for data ingestion

## Project Structure

```
takeHomeProject_Vivpro/
├── app/
│   ├── dao/                          # Data Access Layer
│   │   ├── db_connections/
│   │   │   ├── connection_pool.py    # Connection pool manager
│   │   │   └── pgsql_connection.py   # PostgreSQL connection
│   │   └── song_dao.py               # Song data access object
│   ├── server/                       # API Layer
│   │   ├── __init__.py               # Flask app factory
│   │   └── endpoints.py              # API endpoints
│   └── service/                      # Business Logic Layer
│       ├── dataIngestionService/     # Data import services
│       ├── insert_data.py            # Database data insertion
│       └── song_service.py           # Song business logic
├── config/
│   └── logger_config.py              # Logging configuration
├── tests/
│   └── test.py                       # Unit tests
├── .env                              # Environment variables
├── main.py                           # Application entry point
└── README.md                         # This file
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd takeHomeProject_Vivpro
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip3 install requirements.txt
   ```

4. **Set up PostgreSQL**
   ```bash
   # Create database
   createdb postgres
   
   # Or using psql
   psql -c "CREATE DATABASE postgres;"
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env  # Create from template
   # Edit .env with your database credentials
   ```

## Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=your_username
DB_PASSWORD=your_password

# Connection Pool Configuration
DB_MIN_CONN=2
DB_MAX_CONN=10

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```
## Data Ingestion Service from JSON file
- Run Command ->
  
source .env

PYTHONPATH=. python3 scripts/ingestData.py

## API Endpoints

### 1. Get Song by Title

**Endpoint**: `GET /api/song/<title>`

**Description**: Retrieve song information by title with optional pagination

**Parameters**:
- `title` (path): Song title to search for
- `page` (query, optional): Page number for pagination (default: 1)
- `limit` (query, optional): Items per page (default: 10, max: 100)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "5vYA1mW9g2Coh1HUFUSmlb",
    "title": "3AM",
    "star_rating": 4.5,
    "danceability": 0.484,
    "energy": 0.926,
    "mode": 1,
    "acousticness": 0.0428,
    "tempo": 88.928,
    "duration_ms": 213573,
    "is_rated": true
  }
}
```

**Paginated Response**:
```json
{
  "success": true,
  "data": {
    "songs": [...],
    "search_term": "Love",
    "pagination": {
      "current_page": 1,
      "per_page": 10,
      "total_results": 25,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false,
      "next_page": 2,
      "prev_page": null
    }
  }
}
```

### 2. Rate Song

**Endpoint**: `POST /api/song/<title>/rate`

**Description**: Rate a song with 0-5 stars

**Request Body**:
```json
{
  "rating": 4.5
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "5vYA1mW9g2Coh1HUFUSmlb",
    "title": "3AM",
    "rating": 4.5,
    "message": "Successfully updated rating to 4.5 stars"
  },
  "message": "Successfully rated '3AM' with 4.5 stars"
}
```

### 3. Health Check

**Endpoint**: `GET /health`

**Description**: Check API health status

**Response**:
```json
{
  "status": "healthy",
  "message": "Music API is running"
}
```

## Usage Examples

### Basic Usage

```bash
# Get exact song match
curl "http://localhost:5000/api/song/3AM"

# Get paginated search results
curl "http://localhost:5000/api/song/Love?page=1&limit=5"

# Rate a song
curl -X POST "http://localhost:5000/api/song/3AM/rate" \
     -H "Content-Type: application/json" \
     -d '{"rating": 4.5}'

# Health check
curl "http://localhost:5000/health"
```

### With Special Characters

```bash
# Songs with special characters (URL encoded)
curl "http://localhost:5000/api/song/Special%21%40%23%24%25"

# Rate song with special characters
curl -X POST "http://localhost:5000/api/song/Special%21%40%23%24%25/rate" \
     -H "Content-Type: application/json" \
     -d '{"rating": 4.0}'
```

### Python Client Example

```python
import requests

# Get song
response = requests.get("http://localhost:5000/api/song/3AM")
print(response.json())

# Rate song
rating_data = {"rating": 4.5}
response = requests.post(
    "http://localhost:5000/api/song/3AM/rate",
    json=rating_data
)
print(response.json())
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test.py::TestGetSongByTitleAPI::test_get_song_success -v

# Run with coverage
pytest tests/ --cov=app
```

### Test Categories

- **API Endpoint Tests**: Test all REST endpoints
- **Service Layer Tests**: Test business logic
- **DAO Layer Tests**: Test database operations
- **Integration Tests**: End-to-end testing
- **Error Handling Tests**: Test exception scenarios

## Logging

The application uses structured logging across all layers:

### Log Levels

- **DEBUG**: Detailed tracing, data values
- **INFO**: Important operations, successful requests
- **WARNING**: Non-critical issues, validation failures
- **ERROR**: Exceptions, critical failures

### Log Configuration

Located in `config/logger_config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Viewing Logs

```bash
# Run with debug logging
FLASK_DEBUG=True python main.py

# Filter logs by level
python main.py 2>&1 | grep "ERROR"
```

## 🔧 Development

### Running the Application

```bash
# Development mode
python main.py

# Or with Flask CLI
export FLASK_APP=main.py
flask run

# With specific host/port
python main.py --host 0.0.0.0 --port 8080
```

### Data Ingestion

```bash
# Import song data from CSV
python -m app.service.insert_data

# Or using the data ingestion service
python -m app.service.dataIngestionService.processor
```

### Adding New Features

1. **DAO Layer**: Add database operations in `app/dao/song_dao.py`
2. **Service Layer**: Add business logic in `app/service/song_service.py`
3. **API Layer**: Add endpoints in `app/server/endpoints.py`
4. **Tests**: Add tests in `tests/test.py`

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL status
   pg_ctl status
   
   # Verify credentials in .env file
   psql -h localhost -U your_username -d postgres
   ```

2. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   
   # Kill process or use different port
   export FLASK_PORT=8080
   ```

### Error Response Format

```json
{
  "success": false,
  "message": "Descriptive error message",
  "error": "Technical error details (in 500 errors)"
}
```

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=True
export FLASK_ENV=development
python main.py


