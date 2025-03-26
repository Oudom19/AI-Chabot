from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import re
import random
from ..actions import get_db_connection

class ActionFetchProductAbovePrice(Action):
    def name(self) -> str:
        return "action_fetch_product_above_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates (same as before)
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "I found these {manufacturer} {category} products above ${price:.2f}, sorted by price for your convenience:",
            "Here are some excellent {manufacturer} {category} options above ${price:.2f}, offering premium features:",
            "Take a look at these {manufacturer} {category} models above ${price:.2f}:",
            "I've curated these {manufacturer} {category} picks above ${price:.2f} just for you:",
            "Here are the top {manufacturer} {category} recommendations above ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "I found these {manufacturer} products above ${price:.2f}, sorted by price for your convenience:",
            "Here are some excellent {manufacturer} options above ${price:.2f}, offering premium features:",
            "Take a look at these {manufacturer} models above ${price:.2f}:",
            "I've curated these {manufacturer} picks above ${price:.2f} just for you:",
            "Here are the top {manufacturer} recommendations above ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "I found these {category} products above ${price:.2f}, sorted by price for your convenience:",
            "Here are some excellent {category} options above ${price:.2f}, offering premium features:",
            "Take a look at these {category} models above ${price:.2f}:",
            "I've curated these {category} picks above ${price:.2f} just for you:",
            "Here are the top {category} recommendations above ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "I found these products above ${price:.2f}, sorted by price for your convenience:",
            "Here are some premium options above ${price:.2f}, carefully curated for you:",
            "Take a look at these excellent models above ${price:.2f}:",
            "I've picked these top options above ${price:.2f} for your review:",
            "Here are the best premium picks above ${price:.2f}:"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "I'm sorry, but I couldn’t find any {manufacturer} {category} products above ${price:.2f}. Would you like to explore a lower price range or other categories?",
            "Unfortunately, there are no {manufacturer} {category} options above ${price:.2f} right now. How about trying a lower budget or different categories?",
            "I couldn't locate any {manufacturer} {category} items above ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {manufacturer} {category} above ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {manufacturer} {category} products above ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "I'm sorry, but I couldn’t find any {manufacturer} products above ${price:.2f}. Would you like to explore a lower price range or other categories?",
            "Unfortunately, there are no {manufacturer} options above ${price:.2f} right now. How about trying a lower budget or different categories?",
            "I couldn't locate any {manufacturer} items above ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {manufacturer} above ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {manufacturer} products above ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "I'm sorry, but I couldn’t find any {category} products above ${price:.2f}. Would you like to explore a lower price range or other categories?",
            "Unfortunately, there are no {category} options above ${price:.2f} right now. How about trying a lower budget or different categories?",
            "I couldn't locate any {category} items above ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {category} above ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {category} products above ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "I’m sorry, but I couldn’t find any products above ${price:.2f}. Would you like to try a lower price range?",
            "Unfortunately, there are no options above ${price:.2f} at the moment. How about considering a lower budget?",
            "It seems we don’t have anything above ${price:.2f} right now. Would you like to check a different price range?",
            "No matches found above ${price:.2f}. Would you like to explore a different budget?",
            "We currently don’t have any items above ${price:.2f}. Let me know if you’d like help looking at other ranges!"
        ]

        # Get slots
        price = tracker.get_slot("price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Clean and validate price
        try:
            price = re.sub(r"[^\d.]", "", price)  # Clean price input
            price = float(price)  # Convert price to float
        except ValueError:
            dispatcher.utter_message(
                text="I'm sorry, but I couldn't understand the price you mentioned. Could you please provide a numeric value, like 899 or 1299?"
            )
            return []

        # Determine which intro templates to use based on slots
        if manufacturer and category:
            products_found_intros = PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS
            no_products_found_intros = NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS
        elif manufacturer:
            products_found_intros = PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS
            no_products_found_intros = NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS
        elif category:
            products_found_intros = PRODUCTS_FOUND_WITH_CATEGORY_INTROS
            no_products_found_intros = NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS
        else:
            products_found_intros = PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS
            no_products_found_intros = NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS

        # Fetch products from the database (same as before)
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="I apologize, but I'm unable to access our product database at the moment. Please try again in a few moments or contact our support team if the issue persists."
            )
            return []

        cursor = connection.cursor(dictionary=True)

        # Build the SQL query dynamically based on the available slots
        query = """
            SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE p.price > %s
        """
        params = [price]

        if manufacturer:
            query += " AND m.name = %s"
            params.append(manufacturer)
        if category:
            query += " AND p.category = %s"
            params.append(category)

        query += " ORDER BY p.price ASC LIMIT 5"

        try:
            cursor.execute(query, tuple(params))
        except Exception as e:
            dispatcher.utter_message(
                text="I apologize for the inconvenience, but I encountered an issue while searching for products. Could you please try again in a moment?"
            )
            cursor.close()
            connection.close()
            return []

        products = cursor.fetchall()

        if products:
            # Randomly select an intro message
            intro_template = random.choice(products_found_intros)
            intro_message = intro_template.format(
                manufacturer=manufacturer if manufacturer else "",
                category=category if category else "",
                price=price
            )
            dispatcher.utter_message(text=intro_message)

            # Display product details (same as before)
            for product in products:
                dispatcher.utter_message(
                    text=(
                        f"\n■ Model: {product['model_name']}\n"
                        f"○ Manufacturer: {product['manufacturer']}\n"
                        f"○ Price: ${product['price']:.2f}\n"
                        f"○ Category: {product['category']}\n"
                        f"○ Specifications: {product['cpu']} - {product['ram']} RAM\n"
                        f"○ Storage: {product['storage']}\n"
                    )
                )

            # Follow-up message
            dispatcher.utter_message(
                text=(
                    "These premium models offer excellent features and performance. Let me know if you'd like more details about any specific option.\n"
                    f"🌐 More Info: Visit our website` https://www.ecidisti.com/department/Electronics"
                )
            )
        else:
            # Randomly select a no-products-found intro message
            intro_template = random.choice(no_products_found_intros)
            intro_message = intro_template.format(
                manufacturer=manufacturer if manufacturer else "",
                category=category if category else "",
                price=price
            )
            dispatcher.utter_message(text=intro_message)

        cursor.close()
        connection.close()

        # Clear the manufacturer and category slots after responding
        return [SlotSet("manufacturer", None), SlotSet("category", None)]