from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

EXCEL_PATH = "packaging_inventory.xlsx"

PAR_LEVELS = {
    "Small Box": 30,
    "Medium Box": 40,
    "Large Box": 20,
    "Small Pastry Bag": 100,
    "Medium Pastry Bag": 80,
    "Paper Bread Bag": 60,
    "Plastic Bread Bag": 50
}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    stock_data = data.get("Packaging stock take", {})

    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Item", "Current Stock", "Par Level"])
        df["Item"] = list(PAR_LEVELS.keys())
        df["Current Stock"] = 0
        df["Par Level"] = df["Item"].map(PAR_LEVELS)

    low_items = {}
    for item, qty in stock_data.items():
        qty = int(qty)
        df.loc[df["Item"] == item, "Current Stock"] = qty
        if qty < PAR_LEVELS[item]:
            low_items[item] = qty

    df.to_excel(EXCEL_PATH, index=False)

    if low_items:
        print("LOW STOCK ALERT:", low_items)

    return jsonify({"status": "updated", "low_stock": low_items})