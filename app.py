from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
CORS(app)  # Fix the CORS barrier

DB = "database.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interns (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            role    TEXT    NOT NULL,
            contact TEXT    NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

# GET /api/interns
@app.route("/api/interns", methods=["GET"])
def get_interns():
    conn = get_db()
    interns = conn.execute("SELECT * FROM interns").fetchall()
    conn.close()
    return jsonify([dict(i) for i in interns]), 200

# POST /api/interns
@app.route("/api/interns", methods=["POST"])
def create_intern():
    data = request.get_json()

    if not data or "name" not in data or "role" not in data or "contact" not in data:
        return jsonify({"error": "Bad Request - name, role, contact required"}), 400

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO interns (name, role, contact) VALUES (?, ?, ?)",
            (data["name"], data["role"], data["contact"])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Intern created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Contact already exists"}), 400

# PUT /api/interns/<id>
@app.route("/api/interns/<int:intern_id>", methods=["PUT"])
def update_intern(intern_id):
    data = request.get_json()
    conn = get_db()
    intern = conn.execute(
        "SELECT * FROM interns WHERE id = ?", (intern_id,)
    ).fetchone()

    if not intern:
        conn.close()
        return jsonify({"error": "Intern not found"}), 404

    name    = data.get("name",    intern["name"])
    role    = data.get("role",    intern["role"])
    contact = data.get("contact", intern["contact"])

    conn.execute(
        "UPDATE interns SET name=?, role=?, contact=? WHERE id=?",
        (name, role, contact, intern_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Intern updated"}), 200

# DELETE /api/interns/<id>
@app.route("/api/interns/<int:intern_id>", methods=["DELETE"])
def delete_intern(intern_id):
    conn = get_db()
    intern = conn.execute(
        "SELECT * FROM interns WHERE id = ?", (intern_id,)
    ).fetchone()

    if not intern:
        conn.close()
        return jsonify({"error": "Intern not found"}), 404

    conn.execute("DELETE FROM interns WHERE id = ?", (intern_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Intern deleted"}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)