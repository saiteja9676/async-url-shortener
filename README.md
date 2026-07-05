# Async URL Shortener

A simple asynchronous URL Shortener service that demonstrates REST API development, asynchronous message processing, and relational database operations.

## Tech Stack

- Python
- Flask
- Celery
- Redis
- SQLite
- Marshmallow

## Project Structure

url_shortener/
├── app.py
├── models.py
├── schemas.py
├── tasks.py
├── init_db.py
├── requirements.txt
└── README.md

## Setup Instructions

### 1. Clone the repository
git clone <your-repo-url>
cd url_shortener

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Initialize database
python init_db.py

### 5. Start Redis server
redis-server

### 6. Start Celery worker
celery -A tasks worker --loglevel=info --pool=solo

### 7. Start Flask app
python app.py

## API Endpoints

### POST /shorten
Accepts a URL and returns a short code. Validation happens asynchronously.

Request Body:
{"url": "https://google.com"}

Response (202 ACCEPTED):
{"id": 1, "short_code": "MfQlfE", "url": "https://google.com"}

---

### GET /url/<short_code>
Retrieves URL information by short code.

Response (200 OK):
{"original_url": "https://google.com", "short_code": "MfQlfE", "status": "active"}

Response (404 NOT FOUND):
{"error": "Not found"}

## Sample curl Commands

### POST
curl -i -X POST http://127.0.0.1:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

### GET
curl -i http://127.0.0.1:5000/url/MfQlfE

### GET (invalid code)
curl http://127.0.0.1:5000/url/invalid123

## How It Works

1. Client sends POST /shorten with a URL
2. Flask saves the URL to SQLite with status pending
3. Task is pushed to Redis via Celery
4. Flask returns 202 immediately without waiting
5. Celery worker validates the URL in background
6. Worker updates status to active or invalid in SQLite
7. Client can check status via GET /url/<short_code>

## Architecture

```text
                 Client
                    │
                    ▼
            POST /shorten
                    │
                    ▼
               Flask API
                    │
        Save URL to SQLite
         (status = pending)
                    │
                    ▼
       Celery Task (.delay())
                    │
                    ▼
     Return 202 Accepted to Client
                    │
                    ▼
      Redis (Message Broker)
                    │
                    ▼
            Celery Worker
                    │
              Validate URL
                    │
                    ▼
 Update SQLite (active / invalid)
                    │
                    ▼
      GET /url/<short_code>
```