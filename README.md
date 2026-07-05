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

```text
url_shortener/
├── app.py
├── models.py
├── schemas.py
├── tasks.py
├── init_db.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/saiteja9676/async_url_shortener.git
cd url_shortener
```


### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize the database

```bash
python init_db.py
```

### 6. Start the Redis server

```bash
redis-server
```

### 7. Start the Celery worker

```bash
celery -A tasks worker --loglevel=info --pool=solo
```

### 8. Start the Flask application

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

## Sample API Requests

### POST /shorten

**Request**

```bash
curl -i -X POST http://127.0.0.1:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://google.com"}'
```

**Response**

```http
HTTP/1.1 202 Accepted
```

```json
{
  "id": 1,
  "short_code": "MfQlfE",
  "url": "https://google.com"
}
```

---

### GET /url/<short_code>

**Request**

```bash
curl -i http://127.0.0.1:5000/url/MfQlfE
```

**Response**

```http
HTTP/1.1 200 OK
```

```json
{
  "original_url": "https://google.com",
  "short_code": "MfQlfE",
  "status": "active"
}
```

---

### GET /url/<invalid_code>

**Request**

```bash
curl -i http://127.0.0.1:5000/url/invalid123
```

**Response**

```http
HTTP/1.1 404 Not Found
```

```json
{
  "error": "Not found"
}
```

## How It Works

1. Client sends **POST /shorten** with a URL.
2. Flask generates a unique short code.
3. The URL is stored in SQLite with status **pending**.
4. Flask sends a Celery task to Redis using `.delay()`.
5. Flask immediately returns **HTTP 202 Accepted**.
6. The Celery worker consumes the task from Redis.
7. The worker validates the URL.
8. SQLite is updated with status **active** or **invalid**.
9. Clients can retrieve the current status using **GET /url/<short_code>**.

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