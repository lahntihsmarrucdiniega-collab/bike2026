from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

USER_DB = "users.db"
BIKE_DB = "bike_inventory.db"

# ---------------- DATABASE HELPERS ----------------
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_user_db():
    conn = create_connection(USER_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", ("admin", "1234"))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
    conn.commit()
    conn.close()

def initialize_bike_db():
    conn = create_connection(BIKE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("inventory"))
    return redirect(url_for("login"))

# ---------- AUTH ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = create_connection(USER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            flash(f"Welcome {username}!", "success")
            return redirect(url_for("inventory"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = create_connection(USER_DB)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("User registered successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
        conn.close()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# ---------- BIKE INVENTORY ----------
@app.route("/inventory")
def inventory():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = create_connection(BIKE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bikes ORDER BY id")
    bikes = cursor.fetchall()
    conn.close()
    return render_template("inventory.html", bikes=bikes)

@app.route("/add", methods=["POST"])
def add_bike():
    if "username" not in session:
        return redirect(url_for("login"))

    brand = request.form["brand"]
    model = request.form["model"]
    category = request.form["category"]
    quantity = request.form["quantity"]
    price = request.form["price"]

    if not brand or not model or not category or not quantity or not price:
        flash("All fields are required!", "error")
        return redirect(url_for("inventory"))

    try:
        conn = create_connection(BIKE_DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bikes (brand, model, category, quantity, price) VALUES (?, ?, ?, ?, ?)",
            (brand, model, category, int(quantity), float(price))
        )
        conn.commit()
        conn.close()
        flash("Bike added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")

    return redirect(url_for("inventory"))

@app.route("/update/<int:id>", methods=["POST"])
def update_bike(id):
    if "username" not in session:
        return redirect(url_for("login"))

    brand = request.form["brand"]
    model = request.form["model"]
    category = request.form["category"]
    quantity = request.form["quantity"]
    price = request.form["price"]

    conn = create_connection(BIKE_DB)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bikes SET brand=?, model=?, category=?, quantity=?, price=? WHERE id=?",
        (brand, model, category, int(quantity), float(price), id)
    )
    conn.commit()
    conn.close()
    flash("Bike updated successfully!", "success")
    return redirect(url_for("inventory"))

@app.route("/delete/<int:id>")
def delete_bike(id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = create_connection(BIKE_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bikes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Bike deleted successfully!", "success")
    return redirect(url_for("inventory"))

# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("index.html"), 500

# ---------- MAIN ----------
if __name__ == "__main__":
    initialize_user_db()
    initialize_bike_db()
    app.run(debug=True)
