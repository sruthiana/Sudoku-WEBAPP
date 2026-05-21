from flask import Flask, render_template, request, session, jsonify, redirect
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import sqlite3

from database import init_db
from migrations import migrate


# LOAD ENV VARIABLES
load_dotenv()

app = Flask(__name__)

# JWT CONFIG
# SECRET KEYS
app.secret_key = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# SESSION SECURITY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

jwt = JWTManager(app)

# INIT DB
init_db()
migrate()

def get_db():
    conn = sqlite3.connect("sudoku.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")

# ---------------- REGISTER (UI) ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))
        db.commit()
        db.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN (UI) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"]  # username OR email
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, username, email, password
            FROM users
            WHERE username=? OR email=?
        """, (identifier, identifier))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user[3], password):
            session.clear()
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["email"] = user[2]
            return redirect("/game")
        
        return render_template("login.html",error=("Invalid Credentials"))

    return render_template("login.html")


# ---------------- GAME (UI) ----------------
@app.route("/game")
def game():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        username=session["username"]
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/save_game", methods=["POST"])
def save_game():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO game_stats
        (user_id, difficulty, score, time_taken, mistakes, result)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        data["difficulty"],
        data.get("score", 0),
        data["time"],
        data["mistakes"],
        data["result"]
    ))

    db.commit()
    db.close()

    return jsonify({"status": "saved"})



# ---------------- STATS (UI) ----------------
@app.route("/stats")
def stats():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    cursor = db.cursor()

    # Table stats
    cursor.execute("""
        SELECT
            difficulty,
            COUNT(*) as total_games,
            SUM(CASE WHEN result='Win' THEN 1 ELSE 0 END) as wins,
            MAX(score) as best_score,
            MIN(time_taken) as best_time,
            AVG(mistakes) as avg_mistakes
        FROM game_stats
        WHERE user_id=?
        GROUP BY difficulty
    """, (session["user_id"],))

    stats = cursor.fetchall()

    # Overview stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_games,
            SUM(CASE WHEN result='Win' THEN 1 ELSE 0 END) as wins,
            MIN(time_taken) as best_time
        FROM game_stats
        WHERE user_id=?
    """, (session["user_id"],))

    overview = cursor.fetchone()

    db.close()

    return render_template(
        "stats.html",
        stats=stats,
        overview=overview
    )

# =================================================
# ================= API (JWT) =====================
# =================================================

# -------- API LOGIN --------
@app.route("/api/login", methods=["POST"])
def api_login():
    username = request.json["username"]
    password = request.json["password"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    db.close()

    if user and check_password_hash(user[1], password):
        token = create_access_token(identity=user[0])
        return jsonify(access_token=token)

    return jsonify({"error": "Invalid credentials"}), 401

# -------- PROTECTED API --------
@app.route("/api/protected")
@jwt_required()
def protected():
    return jsonify({"message": "JWT is working!"})

# -------- API LEADERBOARD --------
@app.route("/api/leaderboard")
def api_leaderboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            SELECT
                u.username,
                g.difficulty,
                g.score,
                g.time_taken
            FROM game_stats g
            JOIN users u ON g.user_id = u.id
            ORDER BY g.score DESC, g.time_taken ASC
            LIMIT 10
    """)
    data = cursor.fetchall()
    db.close()

    return jsonify(data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
