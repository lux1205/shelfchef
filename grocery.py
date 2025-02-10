from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database setup
DB_PATH = "products.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            quantity INTEGER NOT NULL,
            alert_sent BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

# Home route
@app.route("/")
def home():
    return render_template("grocery.html")

# Add a new product
@app.route("/add_product", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data.get("name")
    expiry_date = data.get("expiry_date")
    quantity = data.get("quantity")

    if not (name and expiry_date and quantity):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, expiry_date, quantity) VALUES (?, ?, ?)",
            (name, expiry_date, quantity),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Product added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# View all products
@app.route("/view_products", methods=["GET"])
def view_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return jsonify(
        [{"id": row[0], "name": row[1], "expiry_date": row[2], "quantity": row[3], "alert_sent": row[4]} for row in products]
    )

# Check for expiry alerts
@app.route("/check_expiry", methods=["GET"])
def check_expiry():
    today = datetime.now().date()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch products expiring within 3 days or already expired
    cursor.execute(
        "SELECT * FROM products WHERE expiry_date <= ? AND alert_sent = FALSE",
        (today + timedelta(days=3),),
    )
    expiring_products = cursor.fetchall()

    # Update alert_sent status for notified products
    for product in expiring_products:
        cursor.execute(
            "UPDATE products SET alert_sent = TRUE WHERE id = ?",
            (product[0],),
        )
    conn.commit()
    conn.close()

    # Return expiring products
    return jsonify(
        [{"id": row[0], "name": row[1], "expiry_date": row[2], "quantity": row[3]} for row in expiring_products]
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
