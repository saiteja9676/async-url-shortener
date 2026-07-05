import random
import string
from flask import Flask, request, jsonify
from models import get_connection, create_table
from schemas import URLSchema
from tasks import process_url

app = Flask(__name__)
create_table()

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=6))

@app.route("/shorten", methods=["POST"])
def shorten():
    # validate incoming request data
    schema = URLSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify(errors), 400

    url = request.json["url"]

    # generate unique short code
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        short_code = generate_short_code()
        cursor.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,))
        if not cursor.fetchone():
            break

    # insert into DB with staus pending
    cursor.execute(
        "INSERT INTO urls (short_code, original_url, status) VALUES (?, ?, ?)",
        (short_code, url, "pending")
    )
    conn.commit()
    id = cursor.lastrowid
    conn.close()

    # push task to celery worker asynchronously
    process_url.delay(id, short_code, url)

    return jsonify({"id": id, "short_code": short_code, "url": url}), 202

@app.route("/url/<short_code>", methods=["GET"])
def get_url(short_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT short_code, original_url, status FROM urls WHERE short_code = ?",
        (short_code,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error":"Not found"}), 404

    return jsonify({
        "short_code": row[0],
        "original_url": row[1],
        "status": row[2]
    }), 200

if __name__=="__main__":
    app.run(debug=True)