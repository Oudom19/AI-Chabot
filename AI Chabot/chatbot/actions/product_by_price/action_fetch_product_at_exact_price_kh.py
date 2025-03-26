from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import re
import random

class ActionFetchProductAtExactPrice(Action):
    def name(self) -> Text:
        return "action_fetch_product_at_exact_price_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Define intro message templates
        EXACT_INTROS_WITH_MANUFACTURER_AND_CATEGORY = [
            "ល្អណាស់! នេះគឺជាផលិតផល {manufacturer} {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "ដំណឹងល្អ! យើងមានផលិតផល {manufacturer} {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} {category} ដែលត្រូវគ្នានឹងតម្លៃ ${price:.2f} សម្រាប់អ្នក:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "នេះគឺជាផលិតផល {manufacturer} {category} ដែលមានតម្លៃ ${price:.2f}:\n"
        ]

        EXACT_INTROS_WITH_MANUFACTURER = [
            "ល្អណាស់! នេះគឺជាផលិតផល {manufacturer} ដែលមានតម្លៃ ${price:.2f}:\n",
            "ដំណឹងល្អ! យើងមានផលិតផល {manufacturer} ដែលមានតម្លៃ {price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} ដែលត្រូវគ្នានឹងតម្លៃ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} ដែលមានតម្លៃ ${price:.2f}:\n",
            "នេះគឺជាផលិតផល {manufacturer} ដែលមានតម្លៃ ${price:.2f}:\n"
        ]

        EXACT_INTROS_WITH_CATEGORY = [
            "នេះគឺជាផលិតផល {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "ដំណឹងល្អ! យើងមានផលិតផល {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {category} ដែលត្រូវគ្នានឹងតម្លៃ ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផល {category} ដែលមានតម្លៃ ${price:.2f}:\n",
            "នេះគឺជាផលិតផល {category} ដែលមានតម្លៃ ${price:.2f}:\n"
        ]

        EXACT_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY = [
            "នេះគឺជាផលិតផលដែលខ្ញុំបានរកឃើញដែលមានតម្លៃ ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផលដែលត្រូវគ្នានឹងតម្លៃ ${price:.2f}:\n",
            "នេះគឺជាផលិតផលដែលមានតម្លៃ ${price:.2f}:\n",
            "ខ្ញុំបានរកឃើញផលិតផលដែលមានតម្លៃ ${price:.2f}:\n",
            "នេះគឺជាផលិតផលដែលមានតម្លៃ ${price:.2f}:\n"
        ]

        NEAR_INTROS_WITH_MANUFACTURER_AND_CATEGORY = [
            "ទោះបីជាមិនមានផលិតផលដែលត្រូវគ្នាពិតប្រាកដក៏ដោយ នេះគឺជាផលិតផល {manufacturer} {category} ដែលមានតម្លៃក្នុងចន្លោះ ±$100 នៃ ${price:.2f}:\n",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} ដែលមានតម្លៃពិតប្រាកដ ${price:.2f} ទេ ប៉ុន្តែនេះគឺជាជម្រើសដែលនៅក្នុងចន្លោះតម្លៃរបស់អ្នក:\n",
            "នេះគឺជាផលិតផល {manufacturer} {category} ដែលនៅជិតតម្លៃ ${price:.2f} (ក្នុងចន្លោះ $100):\n",
            "គ្មានផលិតផលពិតប្រាកដពី {manufacturer} {category} ប៉ុន្តែផលិតផលទាំងនេះនៅជិតតម្លៃរបស់អ្នក:\n",
            "ខ្ញុំសូមណែនាំផលិតផល {manufacturer} {category} ទាំងនេះដែលនៅជិតតម្លៃ ${price:.2f}:\n"
        ]

        NEAR_INTROS_WITH_MANUFACTURER = [
            "ទោះបីជាមិនមានផលិតផលដែលត្រូវគ្នាពិតប្រាកដក៏ដោយ នេះគឺជាផលិតផល {manufacturer} ដែលមានតម្លៃក្នុងចន្លោះ ±$100 នៃ ${price:.2f}:\n",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} ដែលមានតម្លៃពិតប្រាកដ ${price:.2f} ទេ ប៉ុន្តែនេះគឺជាជម្រើសដែលនៅក្នុងចន្លោះតម្លៃរបស់អ្នក:\n",
            "នេះគឺជាផលិតផល {manufacturer} ដែលនៅជិតតម្លៃ ${price:.2f} (ក្នុងចន្លោះ $100):\n",
            "គ្មានផលិតផលពិតប្រាកដពី {manufacturer} ប៉ុន្តែផលិតផលទាំងនេះនៅជិតតម្លៃរបស់អ្នក:\n",
            "ខ្ញុំសូមណែនាំផលិតផល {manufacturer} ទាំងនេះដែលនៅជិតតម្លៃ ${price:.2f}:\n"
        ]

        NEAR_INTROS_WITH_CATEGORY = [
            "ទោះបីជាមិនមានផលិតផលដែលត្រូវគ្នាពិតប្រាកដក៏ដោយ នេះគឺជាផលិតផល {category} ដែលមានតម្លៃក្នុងចន្លោះ ±$100 នៃ ${price:.2f}:\n\n",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {category} ដែលមានតម្លៃពិតប្រាកដ ${price:.2f} ទេ ប៉ុន្តែនេះគឺជាជម្រើសដែលនៅក្នុងចន្លោះតម្លៃរបស់អ្នក:\n\n",
            "នេះគឺជាផលិតផល {category} ដែលនៅជិតតម្លៃ ${price:.2f} (ក្នុងចន្លោះ $100):\n\n",
            "គ្មានផលិតផលពិតប្រាកដពី {category} ប៉ុន្តែផលិតផលទាំងនេះនៅជិតតម្លៃរបស់អ្នក:\n\n",
            "ខ្ញុំសូមណែនាំផលិតផល {category} ទាំងនេះដែលនៅជិតតម្លៃ ${price:.2f}:\n\n"
        ]

        NEAR_INTROS_WITHOUT_MANUFACTURER_OR_CATEGORY = [
            "ទោះបីជាមិនមានផលិតផលដែលត្រូវគ្នាពិតប្រាកដក៏ដោយ នេះគឺជាជម្រើសដែលនៅក្នុងចន្លោះ ±$100 នៃ ${price:.2f}:\n\n",
            "គ្មានផលិតផលដែលមានតម្លៃពិតប្រាកដ ${price:.2f} ទេ ប៉ុន្តែនេះគឺជាផលិតផលដែលនៅជិតតម្លៃរបស់អ្នក:\n\n",
            "នេះគឺជាផលិតផលដែលនៅជិតតម្លៃ ${price:.2f}:\n\n",
            "ខ្ញុំសូមណែនាំផលិតផលទាំងនេះដែលនៅជិតតម្លៃ ${price:.2f}:\n\n",
            "ខ្ញុំបានរកឃើញជម្រើសទាំងនេះក្នុងចន្លោះ $100 នៃតម្លៃដែលអ្នកបានបញ្ជាក់:\n\n"
        ]

        # Get slots
        price = tracker.get_slot("price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price
        if not price:
            dispatcher.utter_message(
                text="💡 ខ្ញុំរីករាយដែលអាចជួយអ្នករកផលិតផលតាមតម្លៃ។ សូមប្រាប់ខ្ញុំពីចន្លោះតម្លៃដែលអ្នកកំពុងគិត។"
            )
            return []

        try:
            # Clean and convert price to float
            price = re.sub(r"[^\d.]", "", price)  # Remove non-numeric characters except '.'
            price = float(price)  # Convert price to float
        except ValueError:
            dispatcher.utter_message(
                text="❌ សូមទោស ខ្ញុំមិនអាចយល់ពីតម្លៃដែលអ្នកបានបញ្ជាក់។ សូមផ្តល់តម្លៃជាលេខ ឧទាហរណ៍ 899 ឬ 1299។"
            )
            return []

        # Get database connection
        connection = get_db_connection()  # Function to get a database connection
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ ខ្ញុំសុំអភ័យខ្លាំងណាស់! ខ្ញុំមិនអាចភ្ជាប់ទៅទិន្នន័យផលិតផលបានទេ។ សូមព្យាយាមម្ដងទៀតឬទាក់ទងក្រុមការងារគាំទ្ររបស់យើងប្រសិនបើបញ្ហានេះបន្តមាន។"
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
                        f"\n■ Model: {product['model_name']}\n"
                        f"○ Manufacturer: {product['manufacturer']}\n"
                        f"○ Price: ${product['price']:.2f}\n"
                        f"○ Category: {product['category']}\n"
                        f"○ Specifications: {product['cpu']} - {product['ram']} RAM\n"
                        f"○ Storage: {product['storage']}\n"
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
                            f"\n■ {product['model_name']}\n"
                            f"○ Manufacturer: {product['manufacturer']}\n"
                            f"○ Price: ${product['price']:.2f}\n"
                            f"○ Category: {product['category']}\n"
                            f"○ Specifications: {product['cpu']}, {product['ram']} RAM\n"
                            f"○ Storage: {product['storage']}\n"
                        )
                    dispatcher.utter_message(text=response)

                else:
                    # If no near matches are found, inform the user
                    if manufacturer and category:
                        dispatcher.utter_message(
                            text=f"❌ ខ្ញុំសុំអភ័យខ្លាំងណាស់, តែខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} ដែលនៅជុំវិញតម្លៃ ${price:.2f} បានទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទៀតឬពិនិត្យមើលជម្រើសផ្សេងទៀត?"
                        )
                    elif manufacturer:
                        dispatcher.utter_message(
                            text=f"❌ ខ្ញុំសុំអភ័យខ្លាំងណាស់, តែខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} ដែលនៅជុំវិញតម្លៃ ${price:.2f} បានទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទៀតឬពិនិត្យមើលផលិតផលផ្សេងទៀត?"
                        )
                    elif category:
                        dispatcher.utter_message(
                            text=f"❌ ខ្ញុំសុំអភ័យខ្លាំងណាស់, តែខ្ញុំមិនអាចរកឃើញផលិតផល {category} ដែលនៅជុំវិញតម្លៃ ${price:.2f} បានទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទៀតឬពិនិត្យមើលប្រភេទផ្សេងទៀត?"
                        )
                    else:
                        dispatcher.utter_message(
                            text=f"❌ ខ្ញុំសុំអភ័យខ្លាំងណាស់, តែខ្ញុំមិនអាចរកឃើញផលិតផលដែលនៅជុំវិញតម្លៃ ${price:.2f} បានទេ។ តើអ្នកចង់សាកល្បងជួរតម្លៃផ្សេងទៀត?"
                        )

        except Exception as e:
            dispatcher.utter_message(
                text="⚠️ ខ្ញុំសុំអភ័យខ្លាំងណាស់, តែខ្ញុំបានប្រទះជាមួយបញ្ហានៅពេលស្វែងរកផលិតផល។ នេះប្រហែលជាបញ្ហាដែលអាចមានសម្រាប់ពេលសង្ខេប។ តើអ្នកអាចសាកល្បងម្ដងទៀតនៅពេលខ្លះទេ?"
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