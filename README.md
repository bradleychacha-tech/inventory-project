# Inventory Management System

A small admin tool for a retail shop. It has:

- a **Flask REST API** to add, view, update and delete inventory items
- an **OpenFoodFacts** connection to look up product details by barcode or name
- a **command line (CLI) menu** that talks to the API
- **pytest** tests for the API, the CLI and the external API calls

The data is saved in a Python list (an array) while the server runs, so it resets when you restart the server.

## Project structure

```
inventory-project/
├── app.py              # Flask API and the list that acts as the database
├── openfood.py         # functions that call the OpenFoodFacts API
├── cli.py              # command line menu
├── requirements.txt
├── pytest.ini
├── README.md
└── tests/
    ├── conftest.py            # test setup (two starter items)
    ├── test_api.py            # GET, POST, PATCH, DELETE tests
    ├── test_search_routes.py  # tests for search and import routes
    ├── test_openfood.py       # tests for the external API functions
    └── test_cli.py            # tests for the CLI
```

## Installation and setup

You need Python 3 and git.

```bash
git clone <your-repo-link>
cd inventory-project

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Running the project

Use two terminals.

**Terminal 1 - start the API** (runs in Flask debug mode):

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

**Terminal 2 - start the CLI:**

```bash
python cli.py
```

## Data

Each item in the list looks like this. The product fields (`product_name`, `brands`, `ingredients_text`) are the same names OpenFoodFacts uses. `id`, `price` and `stock` are our own fields.

```json
{
  "id": 1,
  "barcode": "3017620422003",
  "product_name": "Nutella Hazelnut Spread",
  "brands": "Ferrero",
  "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa",
  "price": 6.5,
  "stock": 25
}
```

The server starts with 3 items already in the list.

## API endpoints

| Method | Route | What it does | Input | Success output |
|--------|-------|--------------|-------|----------------|
| GET | `/` | Check the API is running | none | message |
| GET | `/inventory` | Get all items | none | list of items (200) |
| GET | `/inventory/<id>` | Get one item | id in the URL | the item (200) |
| POST | `/inventory` | Add a new item | JSON: `product_name` (required), `brands`, `barcode`, `ingredients_text`, `price`, `stock` | the new item (201) |
| PATCH | `/inventory/<id>` | Update an item | JSON with any of: `price`, `stock`, `product_name`, `brands`, `ingredients_text`, `barcode` | the updated item (200) |
| DELETE | `/inventory/<id>` | Delete an item | id in the URL | message (200) |
| GET | `/search/barcode/<barcode>` | Find a product on OpenFoodFacts by barcode (does not save it) | barcode in the URL | product details (200) |
| GET | `/search/name?name=...` | Find a product on OpenFoodFacts by name (does not save it) | `name` query | product details (200) |
| POST | `/inventory/import/<barcode>` | Get a product from OpenFoodFacts and add it to the inventory | barcode in the URL, JSON: `price`, `stock` (both optional, default 0) | the new item (201) |

Errors come back as JSON like `{"error": "Item not found"}`:

- `400` - bad or missing input (for example a negative price)
- `404` - item or product not found
- `502` - OpenFoodFacts could not be reached

### Example requests

```bash
# add an item
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Maize Flour", "brands": "Unga", "price": 2.10, "stock": 40}'

# change the price and stock of item 4
curl -X PATCH http://127.0.0.1:5000/inventory/4 \
  -H "Content-Type: application/json" \
  -d '{"price": 2.50, "stock": 55}'

# delete item 4
curl -X DELETE http://127.0.0.1:5000/inventory/4

# find a product on OpenFoodFacts and add it to the inventory
curl http://127.0.0.1:5000/search/barcode/3017620422003
curl -X POST http://127.0.0.1:5000/inventory/import/3017620422003 \
  -H "Content-Type: application/json" \
  -d '{"price": 6.50, "stock": 20}'
```

## CLI usage

When you run `python cli.py` you see this menu:

```
===== Inventory Menu =====
1. View all items
2. View one item
3. Add a new item
4. Update price or stock
5. Delete an item
6. Find a product on OpenFoodFacts
0. Exit
Choose an option:
```

| Option | What happens | API route used |
|--------|--------------|----------------|
| 1 | Prints every item | `GET /inventory` |
| 2 | Asks for an ID and prints that item with its barcode and ingredients | `GET /inventory/<id>` |
| 3 | Asks for the product details, price and stock, then adds the item | `POST /inventory` |
| 4 | Asks for an ID, then a new price and/or stock (press Enter to skip one) | `PATCH /inventory/<id>` |
| 5 | Asks for an ID and deletes that item | `DELETE /inventory/<id>` |
| 6 | Search OpenFoodFacts by barcode or name, then choose whether to add the product to the inventory | `GET /search/...` and `POST /inventory/import/<barcode>` |

Example of adding and updating an item:

```
Choose an option: 3
Product name: Maize Flour
Brand: Unga
Barcode: 7777777777777
Ingredients: Maize
Enter the price: 2.10
Enter the stock: 40
Item added:
ID: 4 | Name: Maize Flour | Brand: Unga | Price: 2.1 | Stock: 40

Choose an option: 4
Enter the item ID: 4
New price (press Enter to skip):
New stock (press Enter to skip): 55
Item updated:
ID: 4 | Name: Maize Flour | Brand: Unga | Price: 2.1 | Stock: 55
```

Error handling in the CLI:

- if you type letters where a number is needed, it asks again
- if the API is not running, it prints `Cannot connect to the API. Is app.py running?` and the menu keeps working
- if the API or OpenFoodFacts returns an error, the message is printed

## Design notes

| Route | Changes the data? | When the CLI calls it |
|-------|-------------------|-----------------------|
| GET `/inventory` | No | option 1 |
| GET `/inventory/<id>` | No | option 2 |
| POST `/inventory` | Adds an item to the list | option 3 |
| PATCH `/inventory/<id>` | Changes fields of one item | option 4 |
| DELETE `/inventory/<id>` | Removes an item from the list | option 5 |
| GET `/search/barcode/<barcode>` | No | option 6 (search by barcode) |
| GET `/search/name` | No | option 6 (search by name) |
| POST `/inventory/import/<barcode>` | Adds an item using OpenFoodFacts data | option 6, after answering `y` |

New item ids are the biggest id in the list plus 1.

## Running the tests

```bash
pytest
```

The tests never call the real OpenFoodFacts website. `unittest.mock` is used to pretend the API answered, and also to pretend the user typed in the CLI.

- `test_api.py` - GET, POST, PATCH, DELETE and their error cases
- `test_search_routes.py` - search and import routes (found, not found, API down)
- `test_openfood.py` - the OpenFoodFacts functions (found, not found, missing fields, API down)
- `test_cli.py` - every CLI option, bad input and the API not running

## Debugging

- `app.py` runs with `debug=True`, so Flask shows detailed errors and restarts when the code changes.
- You can also test every route in Postman. Set the body to `raw` + `JSON` for POST and PATCH.

## Git workflow

Each feature was built on its own branch and merged into `main`:

- `feature/crud-api` - the CRUD routes and their tests
- `feature/external-api` - OpenFoodFacts functions, search and import routes
- `feature/cli` - the command line menu
- `docs/readme` - this README

The branches were deleted after they were merged.

## Data source

Product data comes from [OpenFoodFacts](https://world.openfoodfacts.org/).
