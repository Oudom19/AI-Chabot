from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
from ..actions import get_db_connection
from rasa_sdk.events import SlotSet

class ActionFetchProductByManufacturer(Action):
    def name(self) -> str:
        return "action_fetch_product_by_manufacturer_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        manufacturer = tracker.get_slot("manufacturer")

        if not manufacturer:
            dispatcher.utter_message(
                text="💡 ខ្ញុំសប្បាយចិត្តសូមបង្ហាញអ្នកផលិតផលពីម៉ាកជាក់លាក់។ តើអ្នកអាចប្រាប់ខ្ញុំបានទេថាតើអ្នកចាប់អារម្មណ៍លើម៉ាកណាខ្លះ?"
            )
            return []

        # Normalize manufacturer name
        manufacturer_normalized = manufacturer.strip()

        # Intro message templates for manufacturer-based search
        MANUFACTURER_FOUND_INTROS = [
            f"ជម្រើសដ៏ល្អ! នេះគឺជាជម្រើសខ្ញុំរកឃើញសម្រាប់ {manufacturer}៖",
            f"បាទ, តើអ្នកកំពុងស្វែងរកផលិតផលពី {manufacturer}? ខ្ញុំមានជម្រើសល្អមួយចំនួនសម្រាប់អ្នក៖",
            f"ដូច្នេះ, នេះគឺជាផលិតផលពី {manufacturer} ដែលអ្នកអាចចូលចិត្ត៖",
        ]

        MANUFACTURER_NOT_FOUND_INTROS = [
            f"❌ ខ្ញុំសោកស្តាយ, តែខ្ញុំមិនអាចស្វែងរកផលិតផលពី {manufacturer} នៅក្នុងទិន្នន័យផលិតផលទេ។",
            f"សូមទោស, ខ្ញុំមិនមានផលិតផលពី {manufacturer} នៅពេលនេះទេ។ តើអ្នកចង់ស្វែងរកម៉ាកផ្សេងទៀតទេ?",
            f"🚫 មើលទៅថាមានផលិតផលពី {manufacturer} មិនមានទេ។ តើអ្នកចង់ស្វែងរកម៉ាកផ្សេងទៀតទេ?",
            f"ឥឡូវនេះមិនមានផលិតផលពី {manufacturer} នៅក្នុងទិន្នន័យទេ។ តើអ្នកចង់ស្វែងរកផលិតផលពីម៉ាកផ្សេងទៀតទេ?"
        ]

        # Connect to the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ ខ្ញុំសូមទោស, ប៉ុន្តែខ្ញុំមិនអាចតភ្ជាប់ទៅនឹងឯកសារ​ទិន្នន័យផលិតផលបានទេ។ សូមព្យាយាមម្តងទៀតក្រោយនេះ ឬទំនាក់ទំនងការគាំទ្រដើម្បីជួយ។"
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
                    "\nតើអ្នកចង់បានព័ត៌មានលម្អិតអំពីផលិតផលណាមួយទេ? សូមប្រាប់ខ្ញុំហើយខ្ញុំនឹងផ្តល់ព័ត៌មានបន្ថែម។\n"
                    f"🌐 ព័ត៌មានបន្ថែម: សូមចូលទៅកាន់គេហទំព័ររបស់យើង https://www.ecidisti.com/department/Electronics\n"
                )

                # Combine everything into one single response
                full_message = f"{intro_message}\n{products_message}"

                # Send the entire response in one call
                dispatcher.utter_message(text=full_message)
                dispatcher.utter_message(text=follow_up_message)
            else:
                # If no products are found
                dispatcher.utter_message(
                    text=random.choice(MANUFACTURER_NOT_FOUND_INTROS).format(manufacturer=manufacturer) + "\n"
                    f"🌐 ព័ត៌មានបន្ថែម: សូមចូលទៅកាន់គេហទំព័ររបស់យើង https://www.ecidisti.com/department/Electronics\n"
                )

        except Exception as e:
            dispatcher.utter_message(
                text="⚙️ ខ្ញុំប្រឈមមុខនឹងបញ្ហានៅពេលស្វែងរកព័ត៌មានផលិតផល។ សូមព្យាយាមម្តងទៀតក្រោយនេះ ឬទំនាក់ទំនងការគាំទ្រដើម្បីជួយប្រសិនបើបញ្ហានេះបន្ត។"
            )
            print(f"Error during the manufacturer product query: {e}")

        # Close the database connection
        cursor.close()
        connection.close()

        return [SlotSet("manufacturer", None)]
