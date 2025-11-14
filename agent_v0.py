import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import Literal, Optional

# ============================================================
# Define structured output schema for Gemini
# ============================================================
class MessageAnalysis(BaseModel):
    intent: Literal["Stock_query", "Dispatch_query", "Payment_update", "Complaint"]
    item: Optional[str] = None
    suggested_reply: str


# ============================================================
# Initialize Gemini model
# ============================================================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key="AIzaSyBV4R1Kc32LplWEyzRpq0_d0WLOmrKA2fU"
)
structured_llm = llm.with_structured_output(
    schema=MessageAnalysis.model_json_schema(),
    method="json_mode"
)


# ============================================================
# Warehouse helpers
# ============================================================
def load_warehouse_data():
    with open("inputs/warehouse_records.json", "r") as f:
        return json.load(f)


def check_stock(item_name: str, location: Optional[str] = None):
    data = load_warehouse_data()
    warehouses = data["warehouses"]

    canonical_list = [p.lower() for p in data["canonical_products"]]
    item_name_lower = item_name.lower()

    matched_item = None
    for canonical in canonical_list:
        if canonical in item_name_lower or item_name_lower in canonical:
            matched_item = canonical
            break

    if not matched_item:
        return "Item not recognized in warehouse database."

    stock_summary = []
    total_qty = 0

    # If location mentioned
    if location and location.lower() in warehouses:
        qty = warehouses[location.lower()].get(matched_item, 0)
        if qty > 0:
            return f"{matched_item.title()} available in {location.title()} warehouse with {qty} units."
        else:
            return f"{matched_item.title()} is out of stock in {location.title()} warehouse."

    # Otherwise summarize all warehouses
    for city, items in warehouses.items():
        if matched_item in items:
            qty = items[matched_item]
            if qty > 0:
                stock_summary.append(f"{city.title()}: {qty}")
                total_qty += qty

    if total_qty == 0:
        return f"{matched_item.title()} is currently out of stock across all warehouses."

    stock_str = ", ".join(stock_summary)
    return f"{matched_item.title()} is in stock — Total {total_qty} units across warehouses ({stock_str})."


# ============================================================
# Core processing function (returns JSON)
# ============================================================
def process_messages(messages_path: str, output_path: str = "output.json"):
    with open(messages_path, "r") as f:
        messages = json.load(f)

    output_data = []

    for msg in messages:
        sender = msg["sender"]
        text = msg["text"]

        prompt = f"""
        Analyze the following customer message and identify:
        1. The intent: one of Stock_query, Dispatch_query, Payment_update, Complaint.
        2. If it's a stock query, extract the item name mentioned.
        3. Generate a polite, helpful suggested reply.

        Message: "{text}"
        """

        response = structured_llm.invoke(prompt)
        intent = response["intent"]
        suggested_reply = response["suggested_reply"]
        item = response.get("item")

        # Detect possible city name
        possible_cities = ["mumbai", "hyderabad", "delhi", "chennai", "kolkata"]
        mentioned_city = next((c for c in possible_cities if c in text.lower()), None)

        # Add warehouse info for stock queries
        if intent == "Stock_query" and item:
            stock_info = check_stock(item, mentioned_city)
            suggested_reply += f" {stock_info}"

        record = {
            "sender": sender,
            "text": text,
            "intent": intent,
            "item": item,
            "reply": suggested_reply
        }

        output_data.append(record)

    # Save output to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(json.dumps(output_data, indent=4, ensure_ascii=False))
    print(f"\n✅ Results saved to {output_path}")

    return output_data
