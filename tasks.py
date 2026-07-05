import sqlite3
import requests
from celery import Celery
from models import get_connection

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_url(id, short_code, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 400:
            status = "active"
        else:
            status = "invalid"
    except Exception:
        status = "invalid"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE urls SET status = ? WHERE id = ?",
        (status, id)
    )
    conn.commit()
    conn.close()