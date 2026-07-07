import requests
from celery import Celery
from models import get_connection

# connect Celery to Redis
app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_url(id, short_code, url):
    try:
        # validate URL
        response = requests.get(url, timeout=5)
        if response.status_code < 400:
            status = "active"
        else:
            status = "invalid"
    except Exception:
        # mark invalid if URL is unreachable
        status = "invalid"

    # update status after validation
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE urls SET status = ? WHERE id = ?",
        (status, id)
    )
    conn.commit()
    conn.close()