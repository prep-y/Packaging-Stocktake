from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

EXCEL_PATH = "packaging_inventory.xlsx"

# Store-specific par levels
PAR_LEVELS = {
    "Doncaster": {
        "Gloves": 100,
        "Hand Soap": 2,
        "Small Box": 30
        # Add the rest manually
    },
    "The Pines": {
        "Gloves": 10,
        "Hand Soap": 1,
        "Small Box": 20
        # Add the rest manually
    },
    "Elwood": {
        "Gloves": 50,
        "Hand Soap": 1.5,
        "Small Box": 25
        # Add the rest manually
    }
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    store = data.get("Store", "Unknown Store")
    stock_data = data.get("Packaging stock take", {})
    par_levels = PAR_LEVELS.get(store, {})

    if not par_levels:
        return jsonify({"error": f"No par levels defined for store: {store}"}), 400

    # Prepare DataFrame (load or initialize)
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Store", "Timestamp", "Item", "Current Stock", "Par Level", "Low Stock"])

    low_items = {}

    # Parse stock data and compare to par levels
    for item, qty in stock_data.items():
        try:
            qty = float(qty)
            par = par_levels.get(item)
            if par is not None:
                is_low = qty < par
                row = {
                    "Store": store,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Item": item,
                    "Current Stock": qty,
                    "Par Level": par,
                    "Low Stock": "Yes" if is_low else "No"
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

                if is_low:
                    low_items[item] = qty
        except ValueError:
            continue  # skip any non-numeric inputs

    df.to_excel(EXCEL_PATH, index=False)

    if low_items:
        print(f"LOW STOCK ({store}):", low_items)

    return jsonify({"status": "updated", "store": store, "low_stock": low_items}), 200