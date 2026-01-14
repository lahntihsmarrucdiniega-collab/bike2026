from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3


app = Flask(__name__)
app.secret_key = "secret_key"  # Needed for flash messages

DB_FILE = "bike_inventory.db"

def create_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = create_connection()
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

# ---------- ROUTES ----------

@app.route("/signup")
def signup():
    # Make sure you have templates/signup.html
    return render_template("signup.html")

@app.route("/")
def index():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bikes ORDER BY id")
    bikes = cursor.fetchall()
    conn.close()
    return render_template("index.html", bikes=bikes)

@app.route("/add", methods=["POST"])
def add_bike():
    brand = request.form["brand"]
    model = request.form["model"]
    category = request.form["category"]
    quantity = request.form["quantity"]
    price = request.form["price"]

    if not brand or not model or not category or not quantity or not price:
        flash("All fields are required!", "error")
        return redirect(url_for("index"))

    try:
        conn = create_connection()
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

    return redirect(url_for("index"))

@app.route("/update/<int:id>", methods=["POST"])
def update_bike(id):
    brand = request.form["brand"]
    model = request.form["model"]
    category = request.form["category"]
    quantity = request.form["quantity"]
    price = request.form["price"]

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bikes SET brand=?, model=?, category=?, quantity=?, price=? WHERE id=?",
        (brand, model, category, int(quantity), float(price), id)
    )
    conn.commit()
    conn.close()
    flash("Bike updated successfully!", "success")
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete_bike(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bikes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Bike deleted successfully!", "success")
    return redirect(url_for("index"))


# ---------- ERROR HANDLER ----------
@app.errorhandler(404)
def page_not_found(e):
    # Make sure you have templates/404.html
    return render_template("register.html"), 404

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)


