from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Your Spoonacular API Key
SPOONACULAR_API_KEY = "ea02f42f32384440ac891d33a223fe5c"

@app.route("/")
def home():
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
    app.run(debug=True)
