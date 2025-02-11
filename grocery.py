from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Data Loads
load_dotenv()
app = Flask(__name__)

# ENV Vars
DB_PATH = "products.db"
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY')

# Home route
@app.route("/")
def index():
    return render_template("lands.html")
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route('/grocery')
def grocery():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('grocery.html', products=products)

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


@app.route("/recipe")
def recipe():
    return render_template("recipe.html")

@app.route("/view_recipes", methods=["GET"])
def view_recipes():
    # Get parameters from the frontend
    ingredients = request.args.get("ingredients")
    diet = request.args.get("diet")  # Vegetarian or Non-Vegetarian
    cuisine = request.args.get("cuisine")  # Cuisine type like Indian or Chinese

    if not ingredients:
        return jsonify({"error": "Please provide some ingredients."}), 400

    # Call Spoonacular API to fetch recipes
    response = requests.get(
        "https://api.spoonacular.com/recipes/complexSearch",
        params={
            "includeIngredients": ingredients,
            "diet": "vegetarian" if diet == "vegetarian" else None,
            "cuisine": cuisine,
            "number": 10,  # Fetch up to 10 recipes
            "apiKey": SPOONACULAR_API_KEY,
        },
    )

    if response.status_code == 200:
        recipes = response.json().get("results", [])
        return jsonify(recipes)
    else:
        return jsonify({"error": "Failed to fetch recipes. Please try again later."}), 500


if __name__ == "__main__":
    # init_db()
    app.run(debug=True)
