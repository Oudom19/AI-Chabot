from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
from ..actions import get_db_connection

class ActionFetchProductByCategory(Action):
    def name(self) -> str:
        return "action_fetch_product_by_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        # Get product category from the user's input
        category = tracker.get_slot("category")

        if not category:
            dispatcher.utter_message(
                text="💡 I'd be happy to assist you with product details. Could you please let me know which product category you're interested in?"
            )
            return []

        # Normalize category by converting to lowercase and stripping whitespace
        category_normalized = category.strip().lower()

        # Define intro message templates for category-based product search
        CATEGORY_FOUND_INTROS = [
            f"Of course, I've found some amazing options in the {category.capitalize()} category! Let me show you a few products that might interest you:",
            f"Yes, here are some great products in the {category.capitalize()} category for you to explore:",
            f"Yeah, check out these top products from our {category.capitalize()} category. They may match your needs:",
            f"Looking for {category.capitalize()} products? Here are some great options to consider:"
        ]

        CATEGORY_NOT_FOUND_INTROS = [
            f"❌ I'm sorry, but I couldn't find any products listed in the {category.capitalize()} category at the moment.",
            f"Unfortunately, there are no products in our {category.capitalize()} category right now. Would you like to explore other categories?",
            f"We don't currently have any items in the {category.capitalize()} category. Would you like to browse other product categories?",
            f"🚫 Looks like there are no products in the {category.capitalize()} category for now. Would you like to check other categories?"
        ]

        # Attempt to connect to the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ I apologize, but we're having trouble connecting to the product database at the moment. Please try again later or contact our support team for further assistance."
            )
            return []

        cursor = connection.cursor(dictionary=True)

        # Query to fetch relevant products in the given category
        query = """
        SELECT p.model_name, p.price, m.name as manufacturer 
        FROM products p 
        JOIN manufacturers m ON p.manufacturer_id = m.id 
        WHERE LOWER(p.category) LIKE %s LIMIT 5
        """
        try:
            cursor.execute(query, (f"%{category_normalized}%",))
            products = cursor.fetchall()
            if products:
                # Construct the "Found" intro message
                intro_message = random.choice(CATEGORY_FOUND_INTROS)

                # Construct the product details in a single formatted string
                product_list = "\n".join(
                    [f"● {product['manufacturer']} - {product['model_name']} - ${product['price']:.2f}" for product in
                     products]
                )

                # Add the follow-up question to the response
                follow_up = (
                    "\nWould you like more details on any of these products? Or perhaps you'd like to explore additional options?\n"
                    f"🌐 More Info: Visit our website https://www.ecidisti.com/department/Electronics\n"
                )
                response = f"{intro_message}\n{product_list}"
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text=follow_up)

            else:
                # No products found: Send a "Not Found" intro message
                dispatcher.utter_message(
                    text=random.choice(CATEGORY_NOT_FOUND_INTROS) + "\n"
                    f"🌐 More Info: Visit our website https://www.ecidisti.com/department/Electronics\n"
                )

        except Exception as e:
            # Handle any database-related exceptions
            dispatcher.utter_message(
                text="⚙️ I encountered an issue while fetching product details. Please try again later, or contact support if the issue persists."
            )
            print(f"Error during product category query: {e}")

        # Close the database cursor and connection
        cursor.close()
        connection.close()

        # Clear the category slot after the action is executed
        return [SlotSet("category", None)]