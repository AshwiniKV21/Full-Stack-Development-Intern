from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory "database"
users = [
    {"id": 101, "profile": {"role": "admin"}},
    {"id": 102, "profile": {"role": "user"}},
]

@app.route("/")
def home():
    return "Flask API is running successfully 🚀"
# ─── GET /users ───────────────────────────────────────────
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users), 200

# ─── GET /users/<id> ──────────────────────────────────────
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

# ─── GET /users/<id>/posts ────────────────────────────────
@app.route("/users/<int:user_id>/posts", methods=["GET"])
def get_user_posts(user_id):
    # Placeholder - would query DB in real app
    return jsonify({"user_id": user_id, "posts": []}), 200

# ─── POST /users ──────────────────────────────────────────
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    # Syntactic Validation (format check)
    if not data:
        return jsonify({"error": "Bad Request - no data provided"}), 400
    if "id" not in data or "profile" not in data:
        return jsonify({"error": "Bad Request - missing fields"}), 400

    # Semantic Validation (logic check)
    if not isinstance(data["id"], int):
        return jsonify({"error": "Bad Request - id must be an integer"}), 400
    if data["profile"].get("role") not in ["admin", "user"]:
        return jsonify({"error": "Bad Request - invalid role"}), 400

    # Check for duplicates
    existing = next((u for u in users if u["id"] == data["id"]), None)
    if existing:
        return jsonify({"error": "User already exists"}), 400

    users.append(data)
    return jsonify({"message": "User created", "user": data}), 201

# ─── PUT /users/<id> ──────────────────────────────────────
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.update(data)
    return jsonify({"message": "User updated", "user": user}), 200

# ─── DELETE /users/<id> ───────────────────────────────────
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": "User deleted"}), 204

# ─── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)