from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import re
import random

class ActionFetchProductAtExactPrice(Action):
    def name(self) -> Text:
        return "action_fetch_product_at_exact_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Define intro message templates
        EXACT_INTROS_WITH_MANUFACTURER_AND_CATEGORY = [
            "Excellent! Here are the {manufacturer} {category} products available exactly at ${price:.2f}:\n\n",
            "Great news! We have the following {manufacturer} {category} models priced precisely at ${price:.2f}:\n\n",
            "I've located these {manufacturer} {category} options matching your exact price of ${price:.2f}:\n\n",
            "You're in luck! I found these {manufacturer} {category} products at exactly ${price:.2f}:\n\n",
            "Perfect match! Here are the {manufacturer} {category} options priced at ${price:.2f}:\n\n"
        ]

        EXACT_INTROS_WITH_MANUFACTURER = [
            "Excellent! Here are the {manufacturer} products available exactly at ${price:.2f}:\n\n",
            "Great news! We have the following {manufacturer} models priced precisely at ${price:.2f}:\n\n",
            "I've located these {manufacturer} options matching your exact price of ${price:.2f}:\n\n",
            "You're in luck! I found these {manufacturer} products at exactly ${price:.2f}:\n\n",
            "Perfect match! Here are the {manufacturer} options priced at ${price:.2f}:\n\n"
        ]

        EXACT_INTROS_WITH_CATEGORY = [
            "Excellent! Here are the {category} products available exactly at ${price:.2f}:\n\n",
            "Great news! We have the following {category} models priced precisely at ${price:.2f}:\n\n",
            "I've located these {category} options matching your exact price of ${price:.2f}:\n\n",
            "You're in luck! I found these {category} products at exactly ${price:.2f}:\n\n",
            "Perfect match! Here are the {category} options priced at ${price:.2f}:\n\n"
        ]

        EXACT_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY = [
            "Here are the products I found at exactly ${price:.2f}:\n\n",
            "I've found the following options matching your exact budget of ${price:.2f}:\n\n",
            "Perfect! Check out these products priced at exactly ${price:.2f}:\n\n",
            "Excellent! I discovered these products at your specified price of ${price:.2f}:\n\n",
            "Right on target! Here are products available for exactly ${price:.2f}:\n\n"
        ]

        NEAR_INTROS_WITH_MANUFACTURER_AND_CATEGORY = [
            "While there are no exact matches, here are some {manufacturer} {category} products within ±$100 of ${price:.2f}:\n\n",
            "I couldn't find {manufacturer} {category} products at exactly ${price:.2f}, but these options are within your range:\n\n",
            "Here are the closest {manufacturer} {category} matches near ${price:.2f} (within $100):\n\n",
            "No exact matches from {manufacturer} {category}, but these products are close to your price:\n\n",
            "Let me suggest these {manufacturer} {category} options around ${price:.2f}:\n\n"
        ]

        NEAR_INTROS_WITH_MANUFACTURER = [
            "While there are no exact matches, here are some {manufacturer} products within ±$100 of ${price:.2f}:\n\n",
            "I couldn't find {manufacturer} products at exactly ${price:.2f}, but these options are within your range:\n\n",
            "Here are the closest {manufacturer} matches near ${price:.2f} (within $100):\n\n",
            "No exact matches from {manufacturer}, but these products are close to your price:\n\n",
            "Let me suggest these {manufacturer} options around ${price:.2f}:\n\n"
        ]

        NEAR_INTROS_WITH_CATEGORY = [
            "While there are no exact matches, here are some {category} products within ±$100 of ${price:.2f}:\n\n",
            "I couldn't find {category} products at exactly ${price:.2f}, but these options are within your range:\n\n",
            "Here are the closest {category} matches near ${price:.2f} (within $100):\n\n",
            "No exact matches from {category}, but these products are close to your price:\n\n",
            "Let me suggest these {category} options around ${price:.2f}:\n\n"
        ]

        NEAR_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY = [
            "While there are no exact matches, here are some options within ±$100 of ${price:.2f}:\n\n",
            "No products at exactly ${price:.2f}, but these are close to your price range:\n\n",
            "Here are the nearest matches I found around ${price:.2f}:\n\n",
            "Let me suggest these products near your budget of ${price:.2f}:\n\n",
            "I found these options within $100 of your specified price:\n\n"
        ]

        # Get slots
        price = tracker.get_slot("price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price
        if not price:
            dispatcher.utter_message(
                text="💡 I'd be happy to help you find products at a specific price point. Could you please let me know what price range you're considering?"
            )
            return []

        try:
            # Clean and convert price to float
            price = re.sub(r"[^\d.]", "", price)  # Remove non-numeric characters except '.'
            price = float(price)  # Convert price to float
        except ValueError:
            dispatcher.utter_message(
                text="❌ I'm sorry, but I couldn't understand the price you mentioned. Could you please provide a numeric value, like 899 or 1299?"
            )
            return []

        # Get database connection
        connection = get_db_connection()  # Function to get a database connection
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ I apologize, but I'm unable to access our product database at the moment. Please try again in a few moments or contact our support team if the issue persists."
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

            # Step 3: Try to find products at the exact price
            query_exact = """
                SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
                FROM products p 
                JOIN manufacturers m ON p.manufacturer_id = m.id 
                WHERE ROUND(p.price, 2) = ROUND(%s, 2)
            """
            params = [price]

            if manufacturer:
                query_exact += " AND LOWER(m.name) = LOWER(%s)"
                params.append(manufacturer.lower())
            if category:
                query_exact += " AND LOWER(p.category) = LOWER(%s)"
                params.append(category.lower())

            query_exact += " LIMIT 5"
            cursor.execute(query_exact, tuple(params))

            # Fetch products at the exact price
            products_exact = cursor.fetchall()

            if products_exact:
                # Determine which intro template to use
                if manufacturer and category:
                    intro_template = random.choice(EXACT_INTROS_WITH_MANUFACTURER_AND_CATEGORY)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category, price=price)
                elif manufacturer:
                    intro_template = random.choice(EXACT_INTROS_WITH_MANUFACTURER)
                    intro_message = intro_template.format(manufacturer=manufacturer, price=price)
                elif category:
                    intro_template = random.choice(EXACT_INTROS_WITH_CATEGORY)
                    intro_message = intro_template.format(category=category, price=price)
                else:
                    intro_template = random.choice(EXACT_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY)
                    intro_message = intro_template.format(price=price)

                # Build the response as a single message
                response = intro_message
                for product in products_exact:
                    response += (
                        f"■ {product['model_name']}\n"
                        f"● Manufacturer: {product['manufacturer']}\n"
                        f"● Price: ${product['price']:.2f}\n"
                        f"● Category: {product['category']}\n"
                        f"● Specifications: {product['cpu']}, {product['ram']} RAM\n"
                        f"● Storage: {product['storage']}\n"
                    )
                dispatcher.utter_message(text=response)

            else:
                # Step 4: If no exact matches are found, search within ±$100
                price_min = price - 100
                price_max = price + 100

                query_range = """
                    SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
                    FROM products p 
                    JOIN manufacturers m ON p.manufacturer_id = m.id 
                    WHERE p.price BETWEEN %s AND %s
                """
                params_range = [price_min, price_max]

                if manufacturer:
                    query_range += " AND LOWER(m.name) = LOWER(%s)"
                    params_range.append(manufacturer.lower())
                if category:
                    query_range += " AND LOWER(p.category) = LOWER(%s)"
                    params_range.append(category.lower())

                query_range += " ORDER BY ABS(p.price - %s) LIMIT 5"
                params_range.append(price)

                cursor.execute(query_range, tuple(params_range))

                # Fetch products within the price range
                products_range = cursor.fetchall()

                if products_range:
                    # Determine which intro template to use
                    if manufacturer and category:
                        intro_template = random.choice(NEAR_INTROS_WITH_MANUFACTURER_AND_CATEGORY)
                        intro_message = intro_template.format(manufacturer=manufacturer, category=category, price=price)
                    elif manufacturer:
                        intro_template = random.choice(NEAR_INTROS_WITH_MANUFACTURER)
                        intro_message = intro_template.format(manufacturer=manufacturer, price=price)
                    elif category:
                        intro_template = random.choice(NEAR_INTROS_WITH_CATEGORY)
                        intro_message = intro_template.format(category=category, price=price)
                    else:
                        intro_template = random.choice(NEAR_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY)
                        intro_message = intro_template.format(price=price)

                    # Build the response as a single message
                    response = intro_message
                    for product in products_range:
                        response += (
                            f"\n■ Model: {product['model_name']}\n"
                            f"○ Manufacturer: {product['manufacturer']}\n"
                            f"○ Price: ${product['price']:.2f}\n"
                            f"○ Category: {product['category']}\n"
                            f"○ Specifications: {product['cpu']} - {product['ram']} RAM\n"
                            f"○ Storage: {product['storage']}\n"
                        )
                    dispatcher.utter_message(text=response)

                else:
                    # If no near matches are found, inform the user
                    if manufacturer and category:
                        dispatcher.utter_message(
                            text=f"❌ I'm sorry, but I couldn't find any {manufacturer} {category} products near the ${price:.2f} price point. Would you like to try a different price range or check other options?"
                        )
                    elif manufacturer:
                        dispatcher.utter_message(
                            text=f"❌ I'm sorry, but I couldn't find any {manufacturer} products near the ${price:.2f} price point. Would you like to try a different price range or check other manufacturers?"
                        )
                    elif category:
                        dispatcher.utter_message(
                            text=f"❌ I'm sorry, but I couldn't find any {category} products near the ${price:.2f} price point. Would you like to try a different price range or check other categories?"
                        )
                    else:
                        dispatcher.utter_message(
                            text=f"❌ I'm sorry, but I couldn't find any products near the ${price:.2f} price point. Would you like to try a different price range?"
                        )

        except Exception as e:
            dispatcher.utter_message(
                text="⚠️ I apologize, but I encountered an issue while searching for products. This might be a temporary problem. Could you please try again in a moment?"
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