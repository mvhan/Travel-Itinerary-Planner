# backend/server.py
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

MAX_DAYS_PER_PROMPT = 3
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"


# ---------- TIỆN ÍCH LƯU/ĐỌC JSON ----------
def load_json(file_path):
    """Đọc file JSON, nếu chưa có thì tạo file rỗng."""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_json(file_path, data):
    """Ghi dữ liệu ra file JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- AUTH: ĐĂNG KÝ & ĐĂNG NHẬP ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    users = load_json(USERS_FILE)
    if any(u["username"] == username for u in users):
        return jsonify({"error": "Username already exists"}), 409

    user_id = len(users) + 1
    users.append({"id": user_id, "username": username, "password": password})
    save_json(USERS_FILE, users)

    return jsonify({"message": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    users = load_json(USERS_FILE)
    for u in users:
        if u["username"] == username and u["password"] == password:
            return jsonify({"message": "Login successful", "user_id": u["id"]}), 200

    return jsonify({"error": "Invalid username or password"}), 401


# ---------- LỊCH SỬ ----------
@app.route("/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    history = load_json(HISTORY_FILE)
    user_history = [h for h in history if h["user_id"] == user_id]
    return jsonify(user_history)


# ---------- SINH ITINERARY ----------
@app.route("/generate", methods=["POST"])
def generate_itinerary():
    try:
        data = request.get_json()
        origin = data.get("origin", "Ha Noi")
        destination = data.get("destination", "Da Lat")
        start_date = data.get("start_date", "2025-11-08")
        end_date = data.get("end_date", "2025-11-10")
        interests = data.get("interests", ["Food"])
        pace = data.get("pace", "Normal")
        user_id = data.get("user_id")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1

        itinerary = {}
        day_chunks = [
            (i, min(i + MAX_DAYS_PER_PROMPT - 1, num_days - 1))
            for i in range(0, num_days, MAX_DAYS_PER_PROMPT)
        ]

        for start_idx, end_idx in day_chunks:
            chunk_days = end_idx - start_idx + 1
            prompt = f"""
You are a travel planner.
Create a {chunk_days}-day itinerary from {origin} to {destination}.
Each day must include Morning, Afternoon, and Evening.
Traveler interests: {', '.join(interests)}. Travel pace: {pace}.
Output in JSON like this:
{{"Day 1": {{"Morning": "...", "Afternoon": "...", "Evening": "..."}}, "Day 2": ...}}
Generate {chunk_days} days starting from Day {start_idx + 1}.
"""
            # Gọi mô hình Mistral qua Ollama
            result = subprocess.run(
                ["ollama", "run", "mistral", prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=180
            )

            raw_output = result.stdout.strip()
            try:
                json_start = raw_output.find('{')
                json_end = raw_output.rfind('}') + 1
                json_text = raw_output[json_start:json_end]
                chunk_itinerary = json.loads(json_text)
                itinerary.update(chunk_itinerary)
            except Exception:
                return jsonify({"error": "Could not parse JSON from model output", "raw_output": raw_output})

        # --- Lưu lịch sử nếu có user_id ---
        if user_id:
            history = load_json(HISTORY_FILE)
            history.append({
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "origin": origin,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "interests": interests,
                "pace": pace,
                "itinerary": itinerary
            })
            save_json(HISTORY_FILE, history)

        return jsonify(itinerary)

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Model timeout. Try shorter prompt or fewer days."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
