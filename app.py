from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

# ---------------- CREATE TEST USER ----------------
def create_test_user():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
    """)

    conn.commit()
    conn.close()

# ---------------- AUTH HELPER ----------------
def login_required():
    return "user_id" in session

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            # ✅ DIRECTLY GO TO TASKS
            return redirect("/tasks")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- TASKS (PAGINATED, LARGE DB SAFE) ----------------
@app.route("/tasks")
def tasks():
    if not login_required():
        return redirect("/login")

    page = int(request.args.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    tasks = cursor.fetchall()
    conn.close()

    return render_template("tasks.html", tasks=tasks, page=page)

@app.route("/add-task", methods=["GET", "POST"])
def add_task():
    if not login_required():
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)",
            (title, description, session["user_id"])
        )
        conn.commit()
        conn.close()

        return redirect("/tasks")

    return render_template("add_task.html")

@app.route("/update-status/<int:task_id>/<status>")
def update_status(task_id, status):
    if not login_required():
        return redirect("/login")

    if status not in ["Pending", "In Progress", "Done"]:
        return redirect("/tasks")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status=? WHERE id=?",
        (status, task_id)
    )
    conn.commit()
    conn.close()

    return redirect("/tasks")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    create_test_user()
    import os

if __name__ == "__main__":
    init_db()
    create_test_user()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

