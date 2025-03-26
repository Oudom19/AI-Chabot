from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import random

class ActionFetchProductBetweenPrices(Action):
    def name(self) -> str:
        return "action_fetch_product_between_prices"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "Here are some {manufacturer} {category} products between ${min_price:.2f} and ${max_price:.2f}, sorted by price (lowest first):",
            "I've found top {manufacturer} {category} picks priced between ${min_price:.2f} and ${max_price:.2f}:",
            "Take a look at these {manufacturer} {category} options between ${min_price:.2f} and ${max_price:.2f}:",
            "Curated {manufacturer} {category} products between ${min_price:.2f} and ${max_price:.2f} for you:",
            "Best {manufacturer} {category} finds between ${min_price:.2f} - ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "Here are some {manufacturer} products between ${min_price:.2f} and ${max_price:.2f}, sorted by price (lowest first):",
            "I've found top {manufacturer} picks priced between ${min_price:.2f} and ${max_price:.2f}:",
            "Take a look at these {manufacturer} options between ${min_price:.2f} and ${max_price:.2f}:",
            "Curated {manufacturer} products between ${min_price:.2f} and ${max_price:.2f} for you:",
            "Best {manufacturer} finds between ${min_price:.2f} - ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "Here are some {category} products between ${min_price:.2f} and ${max_price:.2f}, sorted by price (lowest first):",
            "I've found top {category} picks priced between ${min_price:.2f} and ${max_price:.2f}:",
            "Take a look at these {category} options between ${min_price:.2f} and ${max_price:.2f}:",
            "Curated {category} products between ${min_price:.2f} and ${max_price:.2f} for you:",
            "Best {category} finds between ${min_price:.2f} - ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "Here are some great products priced between ${min_price:.2f} and ${max_price:.2f}, sorted by price:",
            "I've found the best options in your budget range of ${min_price:.2f} to ${max_price:.2f}:",
            "Check out these items priced between ${min_price:.2f} and ${max_price:.2f}:",
            "Curated selections within ${min_price:.2f} to ${max_price:.2f} just for you:",
            "Best finds between ${min_price:.2f} - ${max_price:.2f}:"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "Sorry, no {manufacturer} {category} products found between ${min_price:.2f} and ${max_price:.2f}. Would you like to adjust your range or explore other brands?",
            "Unfortunately, there are no {manufacturer} {category} options in the ${min_price:.2f} - ${max_price:.2f} range. How about increasing your budget or trying a different manufacturer?",
            "I couldn't find any {manufacturer} {category} items between ${min_price:.2f} and ${max_price:.2f}. Shall we try another range or explore other brands?",
            "No matches for {manufacturer} {category} in this price range. Would you like to adjust your range or explore other options?"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "Sorry, no {manufacturer} products found between ${min_price:.2f} and ${max_price:.2f}. Would you like to adjust your range or explore other brands?",
            "Unfortunately, there are no {manufacturer} options in the ${min_price:.2f} - ${max_price:.2f} range. How about increasing your budget or trying a different manufacturer?",
            "I couldn't find any {manufacturer} items between ${min_price:.2f} and ${max_price:.2f}. Shall we try another range or explore other brands?",
            "No matches for {manufacturer} in this price range. Would you like to adjust your range or explore other options?"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "Sorry, no {category} products found between ${min_price:.2f} and ${max_price:.2f}. Would you like to adjust your range or explore other categories?",
            "Unfortunately, there are no {category} options in the ${min_price:.2f} - ${max_price:.2f} range. How about increasing your budget or trying a different category?",
            "I couldn't find any {category} items between ${min_price:.2f} and ${max_price:.2f}. Shall we try another range or explore other categories?",
            "No matches for {category} in this price range. Would you like to adjust your range or explore other options?"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "I'm sorry, but no products were found between ${min_price:.2f} and ${max_price:.2f}. Try adjusting the range?",
            "There are no available options in the price range ${min_price:.2f} - ${max_price:.2f}. Would you like to try increasing your budget?",
            "We don't currently have items priced between ${min_price:.2f} and ${max_price:.2f}. Shall we adjust your selection criteria?",
            "No matches found in ${min_price:.2f} - ${max_price:.2f}. Would you like to try again with a different range?"
        ]

        # Get slots
        min_price = tracker.get_slot("min_price")
        max_price = tracker.get_slot("max_price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price range
        if not min_price or not max_price:
            dispatcher.utter_message(
                text="I'd be happy to search for products in your price range. Could you let me know both your minimum and maximum budget?"
            )
            return []

        try:
            min_price = float(min_price)  # Convert min_price to float
            max_price = float(max_price)  # Convert max_price to float
        except ValueError:
            dispatcher.utter_message(
                text="I'm sorry, but I couldn't understand the price range you specified. Could you provide numeric values, such as 800 to 1200?"
            )
            return []

        # Get database connection
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="I'm unable to access the product database at the moment. Please try again later or contact support for assistance."
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
                WHERE p.price BETWEEN %s AND %s
            """
            params = [min_price, max_price]

            if manufacturer:
                query += " AND LOWER(m.name) = LOWER(%s)"
                params.append(manufacturer.lower())
            if category:
                query += " AND LOWER(p.category) = LOWER(%s)"
                params.append(category.lower())

            query += " ORDER BY p.price ASC LIMIT 5"
            cursor.execute(query, tuple(params))

            # Fetch products within the price range
            products = cursor.fetchall()

            if products:
                # Determine which intro template to use
                if manufacturer and category:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category, min_price=min_price, max_price=max_price)
                elif manufacturer:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, min_price=min_price, max_price=max_price)
                elif category:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_CATEGORY_INTROS)
                    intro_message = intro_template.format(category=category, min_price=min_price, max_price=max_price)
                else:
                    intro_template = random.choice(PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS)
                    intro_message = intro_template.format(min_price=min_price, max_price=max_price)

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
                    text="These options fit perfectly within your budget. Would you like to know more about any specific product?\n"
                         f"🌐 More Info: Visit our website` https://www.ecidisti.com/department/Electronics"
                )
            else:
                # Determine which no-products-found intro template to use
                if manufacturer and category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category, min_price=min_price, max_price=max_price)
                elif manufacturer:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, min_price=min_price, max_price=max_price)
                elif category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS)
                    intro_message = intro_template.format(category=category, min_price=min_price, max_price=max_price)
                else:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS)
                    intro_message = intro_template.format(min_price=min_price, max_price=max_price)

                dispatcher.utter_message(text=intro_message)

        except Exception as e:
            dispatcher.utter_message(
                text="Apologies, but there was an issue fetching the products. Please try again later."
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