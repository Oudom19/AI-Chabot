from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import re
import random

class ActionFetchProductBelowPrice(Action):
    def name(self) -> str:
        return "action_fetch_product_below_price_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} {category} ដែលមានតម្លៃក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អ {manufacturer} {category} តម្លៃក្រោម ${price:.2f}៖",
            "សូមមើលផលិតផល {manufacturer} {category} ក្រោម ${price:.2f}:",
            "ខ្ញុំបានរៀបចំជម្រើស {manufacturer} {category} ក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសល្អបំផុត {manufacturer} {category} តម្លៃក្រោម ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អ {manufacturer} តម្លៃក្រោម ${price:.2f}៖",
            "សូមមើលផលិតផល {manufacturer} ក្រោម ${price:.2f}:",
            "ខ្ញុំបានរៀបចំជម្រើស {manufacturer} ក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសល្អបំផុត {manufacturer} តម្លៃក្រោម ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផល {category} តម្លៃក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អ {category} តម្លៃក្រោម ${price:.2f}៖",
            "សូមមើលផលិតផល {category} ក្រោម ${price:.2f}:",
            "ខ្ញុំបានរៀបចំជម្រើស {category} ក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសល្អបំផុត {category} តម្លៃក្រោម ${price:.2f}:"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "ខ្ញុំបានរកឃើញផលិតផលដែលមានតម្លៃក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសដ៏ល្អដែលមានតម្លៃក្រោម ${price:.2f} ៖",
            "សូមមើលផលិតផលដែលមានតម្លៃក្រោម ${price:.2f}:",
            "ខ្ញុំបានរៀបចំជម្រើសល្អបំផុតក្រោម ${price:.2f} សម្រាប់អ្នក៖",
            "នេះគឺជាជម្រើសល្អបំផុតក្រោម ${price:.2f}:"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} ដែលមានតម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬក៏ប្រភេទផ្សេងទៀតទេ?",
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} {category} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃផ្សេងទៀតទេ?",
            "មិនមានផលិតផល {manufacturer} {category} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់កំណត់ស្វែងរកវិញទេ?",
            "ពេលនេះមិនមានផលិតផល {manufacturer} {category} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងប្រភេទផ្សេងៗទេ?"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬក៏ប្រភេទផ្សេងទៀតទេ?",
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬក៏ប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃផ្សេងទៀតទេ?",
            "មិនមានផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់កំណត់ស្វែងរកវិញទេ?",
            "ពេលនេះមិនមានផលិតផល {manufacturer} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងប្រភេទផ្សេងៗទេ?"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {category} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬក៏ប្រភេទផ្សេងទៀតទេ?",
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផល {category} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះ ឬក៏ប្រភេទផ្សេងទៀតទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផល {category} តម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃផ្សេងទៀតទេ?",
            "មិនមានផលិតផល {category} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់កំណត់ស្វែងរកវិញទេ?",
            "ពេលនេះមិនមានផលិតផល {category} តម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងប្រភេទផ្សេងៗទេ?"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផលណាមួយតម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះទេ?",
            "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញផលិតផលណាមួយតម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះទេ?",
            "ខ្ញុំមិនអាចរកឃើញផលិតផលណាមួយតម្លៃក្រោម ${price:.2f} នៅពេលនេះទេ។ តើអ្នកចង់សាកល្បងតម្លៃផ្សេងទៀតទេ?",
            "មិនមានផលិតផលណាមួយតម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់កំណត់ស្វែងរកវិញទេ?",
            "ពេលនេះមិនមានផលិតផលណាមួយតម្លៃក្រោម ${price:.2f} ទេ។ តើអ្នកចង់សាកល្បងតម្លៃខ្ពស់ជាងនេះទេ?"
        ]

        # Get slots
        price = tracker.get_slot("price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price
        if not price:
            dispatcher.utter_message(
                text="💡 ខ្ញុំរីករាយដែលអាចជួយអ្នករកផលិតផលតាមតម្លៃ។ សូមប្រាប់ខ្ញុំពីតម្លៃដែលអ្នកកំពុងគិត។"
            )
            return []

        try:
            price = re.sub(r"[^\d.]", "", price)  # Clean price input
            price = float(price)  # Convert to float
        except ValueError:
            dispatcher.utter_message(
                text="❌ សូមទោស ខ្ញុំមិនអាចយល់ពីតម្លៃដែលអ្នកបានបញ្ជាក់។ សូមផ្តល់តម្លៃជាលេខ ឧទាហរណ៍ 899 ឬ 1299។"
            )
            return []

        # Get database connection
        connection = get_db_connection()
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
            else:
                # No products found
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
                text="សូមអភ័យទោស មានបញ្ហាក្នុងការស្វែងរកព័ត៌មានផលិតផល។"
            )
            print(f"Error: {e}")
        finally:
            connection.close()

        # Clear the manufacturer and category slots after responding
        return [SlotSet("manufacturer", None), SlotSet("category", None)]
