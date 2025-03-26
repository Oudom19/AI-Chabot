from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
from ..actions import get_db_connection

class ActionFetchProductByCategory(Action):
    def name(self) -> str:
        return "action_fetch_product_by_category_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        # Get product category from the user's input
        category = tracker.get_slot("category")

        if not category:
            dispatcher.utter_message(
                text="💡 ខ្ញុំសប្បាយចិត្តជួយអ្នកអំពីព័ត៌មានផលិតផល។ តើអ្នកអាចប្រាប់ខ្ញុំបានទេថាតើអ្នកចាប់អារម្មណ៍លើប្រភេទផលិតផលណាខ្លះ?"
            )
            return []

        # Normalize category by converting to lowercase and stripping whitespace
        category_normalized = category.strip().lower()

        # Define intro message templates for category-based product search
        CATEGORY_FOUND_INTROS = [
            f"បាទ, នៅក្នុងប្រភេទ {category.capitalize()} ខ្ញុំបានស្វែងរកផលិតផលដែលអាចអាប់ឲ្យអ្នកបាន៖",
            f"យល់ព្រម, សូមមើលផលិតផលក្នុងប្រភេទ {category.capitalize()} ដែលអាចត្រូវការបាន៖",
            f"តើអ្នកកំពុងស្វែងរកផលិតផលប្រភេទ {category.capitalize()} មែនទេ? សូមមើលផលិតផលទាំងនេះ៖"
        ]

        CATEGORY_NOT_FOUND_INTROS = [
            f"សូមទោស, មិនមានផលិតផលនៅក្នុងប្រភេទ {category.capitalize()} នៅពេលនេះទេ។ តើអ្នកចង់ស្វែងរកប្រភេទផ្សេងទៀតទេ?",
            f"ឥឡូវនេះមិនមានផលិតផលក្នុងប្រភេទ {category.capitalize()} ទេ។ តើអ្នកចង់ស្វែងរកប្រភេទផ្សេងទៀតទេ?",
            f"🚫 មើលទៅថាមានផលិតផលនៅក្នុងប្រភេទ {category.capitalize()} មិនមានស្រាប់ទេ។ តើអ្នកចង់ស្វែងរកប្រភេទផ្សេងទៀតទេ?"
        ]

        # Attempt to connect to the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ ខ្ញុំសូមទោស, ប៉ុន្តែមានបញ្ហាក្នុងការតភ្ជាប់ទៅឯកសារ​ទិន្នន័យផលិតផល។ សូមព្យាយាមម្តងទៀតក្រោយទេឬទំនាក់ទំនងជាមួយក្រុមការងារសហគ្រិនសម្រាប់ជំនួយ។"
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
                    "\nតើអ្នកចង់បានព័ត៌មានលម្អិតអំពីផលិតផលណាមួយទេ? ឬតើអ្នកចង់ស្វែងរកជម្រើសផ្សេងទៀត?"
                    f"\n🌐 ព័ត៌មានបន្ថែម: សូមចូលទៅកាន់គេហទំព័ររបស់យើង https://www.ecidisti.com/department/Electronics\n"
                )
                response = f"{intro_message}\n{product_list}"
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text=follow_up)

            else:
                # No products found: Send a "Not Found" intro message
                dispatcher.utter_message(
                    text=random.choice(CATEGORY_NOT_FOUND_INTROS) + "\n"
                    f"🌐 ព័ត៌មានបន្ថែម: សូមចូលទៅកាន់គេហទំព័ររបស់យើង https://www.ecidisti.com/department/Electronics\n"
                )

        except Exception as e:
            # Handle any database-related exceptions
            dispatcher.utter_message(
                text="⚙️ ខ្ញុំប្រឈមមុខនឹងបញ្ហាពេលស្វែងរកព័ត៌មានផលិតផល។ សូមព្យាយាមម្តងទៀតក្រោយនេះ ឬទំនាក់ទំនងការគាំទ្រដើម្បីជួយប្រសិនបើបញ្ហានេះបន្ត។"
            )
            print(f"Error during product category query: {e}")

        # Close the database cursor and connection
        cursor.close()
        connection.close()

        # Clear the category slot after the action is executed
        return [SlotSet("category", None)]
