from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import re
import random
from ..actions import get_db_connection

class ActionFetchProductAbovePrice(Action):
    def name(self) -> str:
        return "action_fetch_product_above_price_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates in Khmer
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "នេះគឺជាជម្រើស {manufacturer} {category} ដ៏ល្អសម្រាប់តម្លៃលើស ${price:.2f}៖",
            "ខ្ញុំបានជ្រើសរើស {manufacturer} {category} ដែលមានតម្លៃលើស ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាការណែនាំសម្រាប់ {manufacturer} {category} ដ៏ល្អបំផុតដែលមានតម្លៃច្រើនជាង${price:.2f}៖"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផលម៉ាក {manufacturer} ដ៏ល្អសម្រាប់តម្លៃច្រើនជាង ${price:.2f}៖",
            "នេះគឺជាជម្រើស {manufacturer} ដែលមានតម្លៃលើស ${price:.2f} សម្រាប់អ្នក៖",
            "ខ្ញុំបានជ្រើសរើស {manufacturer} សម្រាប់តម្លៃលើស ${price:.2f} ពិសេសសម្រាប់អ្នក៖",
            "នេះគឺជាការណែនាំសម្រាប់ម៉ាក {manufacturer} ដែលមានតម្លៃលើស ${price:.2f}៖"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "ខ្ញុំបានរកឃើញ {category} ដែលមានតម្លៃលើស ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើស {category} ដ៏ល្អសម្រាប់តម្លៃច្រើនជាង ${price:.2f} ដែលផ្តល់នូវ៖",
            "ខ្ញុំបានជ្រើសរើស {category} ខាងលើសម្រាប់តម្លៃលើស ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាការណែនាំ {category} ដ៏ល្អបំផុតសម្រាប់តម្លៃ ${price:.2f}៖"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផលខាងលើដែលមានតម្លៃលើស ${price:.2f} របស់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អសម្រាប់តម្លៃលើស ${price:.2f} ដែលត្រូវបានជ្រើសរើសសម្រាប់អ្នក៖",
            "សូមមើលផលិតផលសម្រាប់តម្លៃលើស ${price:.2f}៖",
            "ខ្ញុំបានជ្រើសរើសជម្រើសផលិតផលសម្រាប់តម្លៃច្រើនជាង ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អបំផុតសម្រាប់តម្លៃលើស ${price:.2f}៖"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} ដែលមានតម្លៃលើស ${price:.2f} ទេ។ តើអ្នកចង់ស្វែងរកតម្លៃទាបជាងនេះ ឬប្រភេទផ្សេងទៀតទេ?",
            "មិនមានជម្រើស {manufacturer} {category} ខាងលើតម្លៃ ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងថវិកាទាបជាងនេះ ឬប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} ខាងលើតម្លៃ ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទេ?",
            "គ្មានផលិតផល {manufacturer} {category} ខាងលើតម្លៃ ${price:.2f} ត្រូវបានរកឃើញ។ តើអ្នកចង់កែសម្រួលលក្ខខណ្ឌស្វែងរកទេ?",
            "បច្ចុប្បន្ន យើងគ្មានផលិតផល {manufacturer} {category} ខាងលើតម្លៃ ${price:.2f} ទេ។ ប៉ុន្តែខ្ញុំអាចជួយស្វែងរកជម្រើសផ្សេងទៀតបាន ប្រសិនបើអ្នកចាប់អារម្មណ៍!"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} ខាងលើតម្លៃ ${price:.2f} ទេ។ តើអ្នកចង់ស្វែងរកតម្លៃទាបជាងនេះ ឬប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} ខាងលើតម្លៃ ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទេ?",
            "គ្មានផលិតផល {manufacturer} ខាងលើតម្លៃ ${price:.2f} ត្រូវបានរកឃើញ។ តើអ្នកចង់កែសម្រួលលក្ខខណ្ឌស្វែងរកទេ?",
            "បច្ចុប្បន្ន យើងគ្មានផលិតផល {manufacturer} ខាងលើតម្លៃ ${price:.2f} ទេ។ ប៉ុន្តែខ្ញុំអាចជួយស្វែងរកជម្រើសផ្សេងទៀតបាន ប្រសិនបើអ្នកចាប់អារម្មណ៍!"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចរកឃើញផលិតផល {category} ខាងលើតម្លៃ ${price:.2f} ទេ។ តើអ្នកចង់ស្វែងរកតម្លៃទាបជាងនេះ ឬប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {category} ខាងលើតម្លៃ ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទេ?",
            "គ្មានផលិតផល {category} ខាងលើតម្លៃ ${price:.2f} ត្រូវបានរកឃើញ។ តើអ្នកចង់កែសម្រួលលក្ខខណ្ឌស្វែងរកទេ?",
            "បច្ចុប្បន្ន យើងគ្មានផលិតផល {category} ខាងលើតម្លៃ ${price:.2f} ទេ។ ប៉ុន្តែខ្ញុំអាចជួយស្វែងរកជម្រើសផ្សេងទៀតបាន ប្រសិនបើអ្នកចាប់អារម្មណ៍!"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចរកឃើញផលិតផលណាមួយខាងលើតម្លៃ ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃទាបជាងនេះទេ?",
            "វាហាក់ដូចជាយើងគ្មានអ្វីខាងលើតម្លៃ ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទេ?",
            "គ្មានផលិតផលណាមួយខាងលើតម្លៃ ${price:.2f} ត្រូវបានរកឃើញ។ តើអ្នកចង់ស្វែងរកថវិកាផ្សេងទេ?",
            "បច្ចុប្បន្ន យើងគ្មានផលិតផលណាមួយខាងលើតម្លៃ ${price:.2f} ទេ។ សូមប្រាប់ខ្ញុំប្រសិនបើអ្នកចង់ជួយស្វែងរកជួរផ្សេងទៀត!"
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
                text="ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចយល់តម្លៃដែលអ្នកបានបញ្ជាក់បានទេ។ តើអ្នកអាចផ្តល់តម្លៃលេខ ដូចជា 899 ឬ 1299 បានទេ?"
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

        # Fetch products from the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចចូលប្រើទិន្នន័យផលិតផលរបស់យើងបាននៅពេលនេះទេ។ សូមព្យាយាមម្តងទៀតក្នុងពេលឆាប់ៗនេះ ឬទាក់ទងក្រុមគាំទ្ររបស់យើងប្រសិនបើបញ្ហានេះបន្ត។"
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
                text="ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំបានជួបបញ្ហាក្នុងការស្វែងរកផលិតផល។ តើអ្នកអាចព្យាយាមម្តងទៀតនៅពេលក្រោយបានទេ?"
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

            # Display product details
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
                    "គំរូដ៏ល្អទាំងនេះផ្តល់នូវលក្ខណៈពិសេស និងការអនុវត្តដ៏ល្អ។ សូមប្រាប់ខ្ញុំប្រសិនបើអ្នកចង់ដឹងបន្ថែមអំពីជម្រើសណាមួយ។\n"
                    f"🌐 ព័ត៌មានបន្ថែម៖ សូមមើលក្នុងគេហទំព័ររបស់យើង ` https://www.ecidisti.com/department/Electronics"
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