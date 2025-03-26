from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
from ..actions import get_db_connection
from rasa_sdk.events import SlotSet

class ActionFetchProductByManufacturer(Action):
    def name(self) -> str:
        return "action_fetch_product_by_manufacturer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        manufacturer = tracker.get_slot("manufacturer")

        if not manufacturer:
            dispatcher.utter_message(
                text="💡 I'd be happy to show you products from specific manufacturers. Could you please tell me which brand you're interested in?"
            )
            return []

        # Normalize manufacturer name
        manufacturer_normalized = manufacturer.strip()

        # Intro message templates for manufacturer-based search
        MANUFACTURER_FOUND_INTROS = [
            f"Great choice! Let's explore some products from {manufacturer}. Here are some options I found for you:",
            f"Yes, are you looking for products from {manufacturer}? I've got some top picks for you:",
            f"So, here are some amazing products from {manufacturer} that you might love:",
            f"Lets check out these products from {manufacturer}. I’ve selected a few great options for you:"
        ]

        MANUFACTURER_NOT_FOUND_INTROS = [
            f"❌ I'm sorry, but we couldn't find any products from {manufacturer} in our database at the moment.",
            f"Unfortunately, we don't currently have any products available from {manufacturer}. Would you like to explore other brands?",
            f"🚫 Looks like there are no products from {manufacturer} at the moment. Would you be interested in checking out other manufacturers?",
            f"We currently don't carry any products from {manufacturer}. Would you like to browse products from other brands instead?"
        ]

        # Connect to the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ I apologize, but we're currently unable to connect to the product database. Please try again later or contact support for help."
            )
            return []

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT p.model_name, p.price, p.category 
        FROM products p 
        JOIN manufacturers m ON p.manufacturer_id = m.id 
        WHERE m.name LIKE %s
        ORDER BY p.category, p.price
        LIMIT 10
        """

        try:
            # Query the database
            cursor.execute(query, (f"%{manufacturer_normalized}%",))
            products = cursor.fetchall()

            if products:
                # Select an intro message
                intro_message = random.choice(MANUFACTURER_FOUND_INTROS)

                # Group products by category
                categories = {}
                for product in products:
                    category = product['category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(product)

                # Build the product details
                products_message = "\n".join(
                    [
                        f"\n💻 {category.title()}:\n" + "\n".join(
                            [f"● {product['model_name']} - ${product['price']:.2f}" for product in category_products]
                        ) for category, category_products in categories.items()
                    ]
                )

                # Add the follow-up question
                follow_up_message = (
                    "\nWould you like more details about any specific product? Let me know, and I can provide further specifications.\n"
                    f"🌐 More Info: Visit our website https://www.ecidisti.com/department/Electronics\n"
                )

                # Combine everything into one single response
                full_message = f"{intro_message}\n{products_message}"

                # Send the entire response in one call
                dispatcher.utter_message(text=full_message)
                dispatcher.utter_message(text=follow_up_message)
            else:
                # If no products are found
                dispatcher.utter_message(
                    text=random.choice(MANUFACTURER_NOT_FOUND_INTROS).format(manufacturer=manufacturer).join("\n"
                        f"🌐 More Info: Visit our website https://www.ecidisti.com/department/Electronics"
                    )
                )

        except Exception as e:
            dispatcher.utter_message(
                text="⚙️ I encountered an issue while fetching product details. Please try again later, or contact support if the issue persists."
            )
            print(f"Error during the manufacturer product query: {e}")

        # Close the database connection
        cursor.close()
        connection.close()

        return [SlotSet("manufacturer", None)]