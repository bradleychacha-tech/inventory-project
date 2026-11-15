import requests

API_URL = "http://127.0.0.1:5000"


def show_item(item):
    print(f"ID: {item['id']} | Name: {item['product_name']} | Brand: {item['brands']} "
          f"| Price: {item['price']} | Stock: {item['stock']}")


def show_error(response):
    data = response.json()
    message = data.get("error", "Something went wrong")
    print(f"Error: {message}")


def ask_id():
    while True:
        text = input("Enter the item ID: ")
        try:
            return int(text)
        except ValueError:
            print("The ID must be a whole number.")


def ask_price():
    while True:
        text = input("Enter the price: ")
        try:
            return float(text)
        except ValueError:
            print("The price must be a number.")


def ask_stock():
    while True:
        text = input("Enter the stock: ")
        try:
            return int(text)
        except ValueError:
            print("The stock must be a whole number.")


def view_all():
    response = requests.get(f"{API_URL}/inventory")
    items = response.json()

    if len(items) == 0:
        print("The inventory is empty.")
        return

    for item in items:
        show_item(item)


def view_one():
    item_id = ask_id()
    response = requests.get(f"{API_URL}/inventory/{item_id}")

    if response.status_code == 200:
        item = response.json()
        show_item(item)
        print(f"Barcode: {item['barcode']}")
        print(f"Ingredients: {item['ingredients_text']}")
    else:
        show_error(response)


def add_item():
    name = input("Product name: ")
    brand = input("Brand: ")
    barcode = input("Barcode: ")
    ingredients = input("Ingredients: ")
    price = ask_price()
    stock = ask_stock()

    new_item = {
        "product_name": name,
        "brands": brand,
        "barcode": barcode,
        "ingredients_text": ingredients,
        "price": price,
        "stock": stock
    }
    response = requests.post(f"{API_URL}/inventory", json=new_item)

    if response.status_code == 201:
        print("Item added:")
        show_item(response.json())
    else:
        show_error(response)


def update_item():
    item_id = ask_id()
    changes = {}

    price_text = input("New price (press Enter to skip): ")
    if price_text != "":
        try:
            changes["price"] = float(price_text)
        except ValueError:
            print("The price must be a number.")
            return

    stock_text = input("New stock (press Enter to skip): ")
    if stock_text != "":
        try:
            changes["stock"] = int(stock_text)
        except ValueError:
            print("The stock must be a whole number.")
            return

    if len(changes) == 0:
        print("Nothing to update.")
        return

    response = requests.patch(f"{API_URL}/inventory/{item_id}", json=changes)

    if response.status_code == 200:
        print("Item updated:")
        show_item(response.json())
    else:
        show_error(response)


def delete_item():
    item_id = ask_id()
    response = requests.delete(f"{API_URL}/inventory/{item_id}")

    if response.status_code == 200:
        print("Item deleted.")
    else:
        show_error(response)


def find_on_api():
    print("1. Search by barcode")
    print("2. Search by name")
    choice = input("Choose 1 or 2: ")

    if choice == "1":
        barcode = input("Enter the barcode: ").strip()
        response = requests.get(f"{API_URL}/search/barcode/{barcode}")
    elif choice == "2":
        name = input("Enter the product name: ").strip()
        response = requests.get(f"{API_URL}/search/name", params={"name": name})
    else:
        print("Please choose 1 or 2.")
        return

    if response.status_code != 200:
        show_error(response)
        return

    product = response.json()
    print(f"Found: {product['product_name']} | Brand: {product['brands']}")
    print(f"Barcode: {product['barcode']}")
    print(f"Ingredients: {product['ingredients_text']}")

    answer = input("Add this product to the inventory? (y/n): ")
    if answer.lower() != "y":
        return

    if product["barcode"] == "":
        print("This product has no barcode so it cannot be added.")
        return

    price = ask_price()
    stock = ask_stock()
    response = requests.post(
        f"{API_URL}/inventory/import/{product['barcode']}",
        json={"price": price, "stock": stock}
    )

    if response.status_code == 201:
        print("Item added:")
        show_item(response.json())
    else:
        show_error(response)


def main():
    while True:
        print()
        print("===== Inventory Menu =====")
        print("1. View all items")
        print("2. View one item")
        print("3. Add a new item")
        print("4. Update price or stock")
        print("5. Delete an item")
        print("6. Find a product on OpenFoodFacts")
        print("0. Exit")
        choice = input("Choose an option: ")

        try:
            if choice == "1":
                view_all()
            elif choice == "2":
                view_one()
            elif choice == "3":
                add_item()
            elif choice == "4":
                update_item()
            elif choice == "5":
                delete_item()
            elif choice == "6":
                find_on_api()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please try again.")
        except requests.exceptions.ConnectionError:
            print("Cannot connect to the API. Is app.py running?")


if __name__ == "__main__":
    main()
