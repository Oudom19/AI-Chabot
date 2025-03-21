import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
from rasa_sdk.events import SlotSet

def clear_all_slots():
    return [
        SlotSet("manufacturer", None),
        SlotSet("category", None),
        SlotSet("model_name", None),
        SlotSet("cpu", None),
        SlotSet("ram", None)
    ]

# Helper function for database connection
def execute_query(query, params):
    connection = get_db_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()

# Response intros
INTRO_MESSAGES = [
    "Certainly! Here’s what I found:",
    "Absolutely! Here’s the information you requested:",
    "Of course! Here’s what we have:",
    "Sure! Here’s the relevant information:",
    "Yes! Allow me to share the details with you:"
]

# ---- Class 1: Handling Manufacturer + Category Query ----
class ActionCheckManufacturerCategory(Action):
    def name(self) -> Text:
        return "action_check_manufacturer_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        if not manufacturer or not category:
            dispatcher.utter_message(text="Please specify both a manufacturer and a category.")
            return clear_all_slots()

        query = """
            SELECT p.model_name 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(m.name) = LOWER(%s) AND LOWER(p.category) = LOWER(%s)
        """
        models = execute_query(query, (manufacturer.lower(), category.lower()))

        if models:
            model_list = ", ".join([model["model_name"] for model in models])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" {manufacturer} offers the following models in {category}: {model_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "Do these manufacturers and categories match what you're looking for?",
                "Would you like to see more products from these manufacturers and categories?",
                "Do you want to explore other manufacturers or categories?",
                "Are you interested in checking more brands or product types?",
                "Would you like recommendations for similar manufacturers and categories?",
                "Do you need help finding more options from these manufacturers or in this category?",
                "Are these the right manufacturers and categories, or do you want to see more?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"I’m sorry, but we don’t have any {category} products from {manufacturer} right now.")

        return clear_all_slots()

# ---- Class 2: Handling Manufacturer Query ----
class ActionCheckManufacturer(Action):
    def name(self) -> Text:
        return "action_check_manufacturer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        manufacturer = tracker.get_slot("manufacturer")

        if not manufacturer:
            dispatcher.utter_message(text="Please specify a manufacturer.")
            return clear_all_slots()

        query = """
            SELECT DISTINCT p.category 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(m.name) = LOWER(%s)
        """
        categories = execute_query(query, (manufacturer.lower(),))

        if categories:
            category_list = ", ".join([cat["category"] for cat in categories])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" {manufacturer} offers products in the following categories: {category_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "Does this match what you're looking for?",
                "Are these the products you were interested in?",
                "Would you like more details on any of these products?",
                "Do any of these options fit your needs?",
                "Would you like to explore similar products from other manufacturers?",
                "Do you need specifications or pricing details on any of these?",
                "Are you looking for more options from this manufacturer?",
                "Would you like recommendations based on these products?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"Unfortunately, we don’t have any products from {manufacturer} at the moment.")

        return clear_all_slots()

# ---- Class 3: Handling Category Query ----
class ActionCheckCategory(Action):
    def name(self) -> Text:
        return "action_check_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("category")

        if not category:
            dispatcher.utter_message(text="Please specify a category.")
            return clear_all_slots()

        query = """
            SELECT DISTINCT m.name as manufacturer 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(p.category) = LOWER(%s)
        """
        manufacturers = execute_query(query, (category.lower(),))

        if manufacturers:
            manu_list = ", ".join([manu["manufacturer"] for manu in manufacturers])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" We have {category} products from {manu_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "Does this category include what you're looking for?",
                "Are you interested in exploring more products in this category?",
                "Would you like to see more options from this category?",
                "Does this category match your needs, or would you like to check another one?",
                "Are you looking for different types of products within this category?",
                "Would you like recommendations for other categories?",
                "Do you need more details about products in this category?",
                "Would you like to explore other related categories?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"I’m sorry, but we currently don’t have {category} products in stock.")

        return clear_all_slots()

# ---- Class 4: Handling Model Name Query ----
class ActionCheckModel(Action):
    def name(self) -> Text:
        return "action_check_model"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        model_name = tracker.get_slot("model_name")

        if not model_name:
            dispatcher.utter_message(text="Please specify a model name.")
            return clear_all_slots()

        query = """
            SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(p.model_name) = LOWER(%s) 
        """
        products = execute_query(query, (model_name.lower(),))

        if products:
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + "\n")
            for product in products:
                dispatcher.utter_message(
                    text=(
                        f"■ {product['model_name']}\n"
                        f"● Manufacturer: {product['manufacturer']}\n"
                        f"● Price: ${product['price']:.2f}\n"
                        f"● Category: {product['category']}\n"
                        f"● CPU: {product['cpu']}\n"
                        f"● RAM: {product['ram']}\n"
                        f"● Storage: {product['storage']}\n"
                    )
                )
            # Follow-up question (only one)
            follow_up_questions = [
                "Are these the products you were looking for?",
                "Would you like more details on any of these products?",
                "Do any of these products match your needs?",
                "Would you like to see more products like these?",
                "Do you need additional information on any of these products?",
                "Would you like to explore other product options?",
                "Are you interested in similar products with different specifications?",
                "Would you like recommendations for other products that might suit your needs?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"I’m sorry, but I couldn’t find any details for {model_name}.")

        return clear_all_slots()