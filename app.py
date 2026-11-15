# app.py
# Inventory API for a small retail shop.

from flask import Flask, jsonify, request

app = Flask(__name__)

# This list is our fake database.
# The product fields (name, brands, ingredients) look like OpenFoodFacts data.
# id, price and stock are our own fields.
inventory = [
    {
        "id": 1,
        "barcode": "3017620422003",
        "product_name": "Nutella Hazelnut Spread",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa",
        "price": 6.50,
        "stock": 25
    },
    {
        "id": 2,
        "barcode": "5449000000996",
        "product_name": "Coca-Cola",
        "brands": "Coca-Cola",
        "ingredients_text": "Carbonated water, sugar, colour caramel, phosphoric acid, natural flavourings",
        "price": 1.20,
        "stock": 80
    },
    {
        "id": 3,
        "barcode": "1234567890123",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 3.99,
        "stock": 12
    }
]


def find_item(item_id):
    # look for an item with this id, return None if it is not there
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def make_new_id():
    # the new id is the biggest id we have plus 1
    biggest = 0
    for item in inventory:
        if item["id"] > biggest:
            biggest = item["id"]
    return biggest + 1


def price_is_ok(price):
    return isinstance(price, (int, float)) and price >= 0


def stock_is_ok(stock):
    return isinstance(stock, int) and stock >= 0


def add_to_inventory(barcode, name, brands, ingredients, price, stock):
    new_item = {
        "id": make_new_id(),
        "barcode": barcode,
        "product_name": name,
        "brands": brands,
        "ingredients_text": ingredients,
        "price": price,
        "stock": stock
    }
    inventory.append(new_item)
    return new_item


# ---------- Routes ----------

@app.route("/")
def home():
    return jsonify({"message": "Inventory API is running"})


# GET all items
@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(inventory), 200


# GET one item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


# POST a new item
@app.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json(silent=True)
    if data is None or not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    price = data.get("price", 0)
    stock = data.get("stock", 0)

    if not price_is_ok(price):
        return jsonify({"error": "price must be a number that is 0 or more"}), 400
    if not stock_is_ok(stock):
        return jsonify({"error": "stock must be a whole number that is 0 or more"}), 400

    new_item = add_to_inventory(
        data.get("barcode", ""),
        data["product_name"],
        data.get("brands", ""),
        data.get("ingredients_text", ""),
        price,
        stock
    )
    return jsonify(new_item), 201


# PATCH (update) an item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Please send JSON data"}), 400

    # check the numbers first so we do not update only half of the item
    if "price" in data and not price_is_ok(data["price"]):
        return jsonify({"error": "price must be a number that is 0 or more"}), 400
    if "stock" in data and not stock_is_ok(data["stock"]):
        return jsonify({"error": "stock must be a whole number that is 0 or more"}), 400

    if "price" in data:
        item["price"] = data["price"]
    if "stock" in data:
        item["stock"] = data["stock"]
    if "product_name" in data:
        item["product_name"] = data["product_name"]
    if "brands" in data:
        item["brands"] = data["brands"]
    if "ingredients_text" in data:
        item["ingredients_text"] = data["ingredients_text"]
    if "barcode" in data:
        item["barcode"] = data["barcode"]

    return jsonify(item), 200


# DELETE an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


if __name__ == "__main__":
    # debug=True turns on Flask debug mode
    app.run(debug=True)
