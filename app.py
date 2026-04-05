import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "database.db"

# ─── Setup Database ───────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            UserID   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name     TEXT    NOT NULL,
            Email    TEXT    NOT NULL UNIQUE,
            Age      INTEGER CHECK (Age >= 18)
        );

        CREATE TABLE IF NOT EXISTS orders (
            OrderID  INTEGER PRIMARY KEY AUTOINCREMENT,
            Total    REAL    NOT NULL,
            UserID   INTEGER NOT NULL,
            FOREIGN KEY (UserID) REFERENCES users(UserID)
        );
    """)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    return conn



# ─── USERS CRUD ───────────────────────────────────────────

# CREATE - POST /users
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    # Syntactic validation
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Bad Request - name and email required"}), 400

    # Semantic validation
    if not isinstance(data["name"], str) or not isinstance(data["email"], str):
        return jsonify({"error": "Bad Request - invalid data types"}), 400

    try:
        conn = get_db()
        # Parameterized query - prevents SQL injection
        conn.execute(
            "INSERT INTO users (Name, Email) VALUES (?, ?)",
            (data["name"], data["email"])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User created"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400


# READ - GET /users
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users]), 200


# READ - GET /users/<id>
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE UserID = ?", (user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user)), 200


# READ - GET /users/<id>/posts (orders)
@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_user_orders(user_id):
    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE UserID = ?", (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders]), 200


# UPDATE - PUT /users/<id>
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request - no data"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE UserID = ?", (user_id,)
    ).fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    name  = data.get("name",  user["Name"])
    email = data.get("email", user["Email"])

    try:
        conn.execute(
            "UPDATE users SET Name = ?, Email = ? WHERE UserID = ?",
            (name, email, user_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User updated"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400


# DELETE - DELETE /users/<id>
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE UserID = ?", (user_id,)
    ).fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.execute("DELETE FROM users WHERE UserID = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted"}), 204


# ─── ORDERS CRUD ──────────────────────────────────────────

# CREATE - POST /orders
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data or "total" not in data or "user_id" not in data:
        return jsonify({"error": "Bad Request - total and user_id required"}), 400

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO orders (Total, UserID) VALUES (?, ?)",
            (data["total"], data["user_id"])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Order created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Invalid UserID - user does not exist"}), 400


# READ - GET /orders
@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_db()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders]), 200


# ─── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True)