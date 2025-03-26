from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import re
import random

class ActionFetchProductBelowPrice(Action):
    def name(self) -> str:
        return "action_fetch_product_below_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "I found these {manufacturer} {category} products under ${price:.2f}, sorted by value for your convenience:",
            "Here are some excellent {manufacturer} {category} options under ${price:.2f}, offering great value:",
            "Take a look at these {manufacturer} {category} models under ${price:.2f}:",
            "I've curated these {manufacturer} {category} picks under ${price:.2f} just for you:",
            "Here are the top {manufacturer} {category} recommendations under ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "I found these {manufacturer} products under ${price:.2f}, sorted by value for your convenience:",
            "Here are some excellent {manufacturer} options under ${price:.2f}, offering great value:",
            "Take a look at these {manufacturer} models under ${price:.2f}:",
            "I've curated these {manufacturer} picks under ${price:.2f} just for you:",
            "Here are the top {manufacturer} recommendations under ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "I found these {category} products under ${price:.2f}, sorted by value for your convenience:",
            "Here are some excellent {category} options under ${price:.2f}, offering great value:",
            "Take a look at these {category} models under ${price:.2f}:",
            "I've curated these {category} picks under ${price:.2f} just for you:",
            "Here are the top {category} recommendations under ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "I found these products under ${price:.2f}, sorted to highlight the best value:",
            "Here are some great options under ${price:.2f}, carefully curated for you:",
            "Take a look at these excellent models under ${price:.2f}:",
            "I've picked these top options under ${price:.2f} for your review:",
            "Here are the best value picks under ${price:.2f}:"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "I'm sorry, but I couldn’t find any {manufacturer} {category} products under ${price:.2f}. Would you like to explore a higher price range or other categories?",
            "Unfortunately, there are no {manufacturer} {category} options under ${price:.2f} right now. How about trying a higher budget or different categories?",
            "I couldn't locate any {manufacturer} {category} items under ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {manufacturer} {category} under ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {manufacturer} {category} products under ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "I'm sorry, but I couldn’t find any {manufacturer} products under ${price:.2f}. Would you like to explore a higher price range or other brands?",
            "Unfortunately, there are no {manufacturer} options under ${price:.2f} right now. How about trying a higher budget or different manufacturers?",
            "I couldn't locate any {manufacturer} items under ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {manufacturer} under ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {manufacturer} products under ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "I'm sorry, but I couldn’t find any {category} products under ${price:.2f}. Would you like to explore a higher price range or other categories?",
            "Unfortunately, there are no {category} options under ${price:.2f} right now. How about trying a higher budget or different categories?",
            "I couldn't locate any {category} items under ${price:.2f} at the moment. Would you like to try a different price range?",
            "No matches found for {category} under ${price:.2f}. Would you like to adjust the search criteria?",
            "We currently have no {category} products under ${price:.2f}, but I can help explore other options if you're interested!"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "I’m sorry, but I couldn’t find any products under ${price:.2f}. Would you like to try a higher price range?",
            "Unfortunately, there are no options under ${price:.2f} at the moment. How about considering a higher budget?",
            "It seems we don’t have anything under ${price:.2f} right now. Would you like to check a different price range?",
            "No matches found under ${price:.2f}. Would you like to explore a different budget?",
            "We currently don’t have any items under ${price:.2f}. Let me know if you’d like help looking at other ranges!"
        ]

        # Get slots
        price = tracker.get_slot("price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price
        if not price:
            dispatcher.utter_message(
                text="I'd be happy to help you find budget-friendly options. Could you please let me know your maximum budget?"
            )
            return []

        try:
            price = re.sub(r"[^\d.]", "", price)  # Clean price input
            price = float(price)  # Convert to float
        except ValueError:
            dispatcher.utter_message(
                text="I'm sorry, but I couldn't understand the price you mentioned. Could you provide a numeric value, like 899 or 1299?"
            )
            return []

        # Get database connection
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="I’m sorry, but I couldn’t access our product database at this time. Please try again later or contact support for assistance."
            )
            return []

        cursor = connection.cursor(dictionary=True)

        try:
            # Step 1: Fetch all manufacturers from the database
            cursor.execute("SELECT LOWER(name) as name FROM manufacturers")
            manufacturers_in_db = [row["name"] for row in cursor.fetchall()]

            # Step 2: Check if the user explicitly mentioned a manufacturer in the current query
            latest_message = tracker.latest_message.get("text", "").lower()
            manufacturer_mentioned = any(
                manufacturer_name in latest_message for manufacturer_name in manufacturers_in_db
            )

            # Reset manufacturer slot if not explicitly mentioned
            if not manufacturer_mentioned:
                manufacturer = None

            # Step 3: Build the SQL query dynamically based on the available slots
            query = """
                SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
                FROM products p 
                JOIN manufacturers m ON p.manufacturer_id = m.id 
                WHERE p.price < %s
            """
            params = [price]

            if manufacturer:
                query += " AND LOWER(m.name) = LOWER(%s)"
                params.append(manufacturer.lower())
            if category:
                query += " AND LOWER(p.category) = LOWER(%s)"
                params.append(category.lower())

            query += " ORDER BY p.price DESC LIMIT 5"
            cursor.execute(query, tuple(params))

            # Fetch products below the specified price
            products = cursor.fetchall()

            if products:
                # Determine which intro template to use
                if manufacturer and category:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category, price=price)
                elif manufacturer:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, price=price)
                elif category:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_CATEGORY_INTROS)
                    intro_message = intro_template.format(category=category, price=price)
                else:
                    intro_template = random.choice(PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS)
                    intro_message = intro_template.format(price=price)

                # Build the response as a single message
                response = intro_message
                for product in products:
                    response += (
                        f"\n■ Model: {product['model_name']}\n"
                        f"○ Manufacturer: {product['manufacturer']}\n"
                        f"○ Price: ${product['price']:.2f}\n"
                        f"○ Category: {product['category']}\n"
                        f"○ Specifications: {product['cpu']} - {product['ram']} RAM\n"
                        f"○ Storage: {product['storage']}\n"
                    )
                dispatcher.utter_message(text=response)

                # Follow-up message
                dispatcher.utter_message(
                    text="These options are great value for their price. Would you like more details about any specific product?\n"
                         f"🌐 More Info: Visit our website` https://www.ecidisti.com/department/Electronics"
                )
            else:
                # Determine which no-products-found intro template to use
                if manufacturer and category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category, price=price)
                elif manufacturer:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, price=price)
                elif category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS)
                    intro_message = intro_template.format(category=category, price=price)
                else:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS)
                    intro_message = intro_template.format(price=price)

                dispatcher.utter_message(text=intro_message)

        except Exception as e:
            dispatcher.utter_message(
                text="I ran into an issue while searching for products. Please try again in a moment."
            )
            print(f"Error fetching products: {str(e)}")
        finally:
            # Close database connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        # Clear the manufacturer and category slots after responding
        return [SlotSet("manufacturer", None), SlotSet("category", None)]