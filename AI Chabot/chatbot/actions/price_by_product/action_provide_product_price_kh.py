from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import random

class ActionProvideProductPrice(Action):
    def name(self) -> Text:
        return "action_provide_product_price_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract slot values
        model_name = tracker.get_slot("model_name")
        ram = tracker.get_slot("ram")
        cpu = tracker.get_slot("cpu")
        storage = tracker.get_slot("storage")

        if not model_name:
            dispatcher.utter_message(
                text="ខ្ញុំរីករាយដែលអាចជួយអ្នកពិនិត្យតម្លៃ។ តើអ្នកអាចប្រាប់ខ្ញុំពីម៉ូដែលជាក់លាក់ដែលអ្នកចាប់អារម្មណ៍បានទេ?"
            )
            return []

        # Fetch the product price from the database
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចចូលប្រើទិន្នន័យផលិតផលរបស់យើងបាននៅពេលនេះ។ សូមព្យាយាមម្តងទៀតក្នុងពេលឆាប់ៗនេះ ឬទាក់ទងក្រុមគាំទ្ររបស់យើងប្រសិនបើបញ្ហានេះបន្ត។"
            )
            return []

        cursor = connection.cursor(dictionary=True)

        # Define a list of conditions to try, prioritizing the most specific combinations
        conditions = [
            # Match with model_name, ram, cpu, and storage (most specific)
            ("p.model_name = %s AND p.ram = %s AND p.cpu = %s AND p.storage = %s",
             [model_name, ram, cpu, storage]),
            # Match with model_name, ram, and cpu
            ("p.model_name = %s AND p.ram = %s AND p.cpu = %s",
             [model_name, ram, cpu]),
            # Match with model_name, ram, and storage
            ("p.model_name = %s AND p.ram = %s AND p.storage = %s",
             [model_name, ram, storage]),
            # Match with model_name, cpu, and storage
            ("p.model_name = %s AND p.cpu = %s AND p.storage = %s",
             [model_name, cpu, storage]),
            # Match with model_name and ram
            ("p.model_name = %s AND p.ram = %s",
             [model_name, ram]),
            # Match with model_name and cpu
            ("p.model_name = %s AND p.cpu = %s",
             [model_name, cpu]),
            # Match with model_name and storage
            ("p.model_name = %s AND p.storage = %s",
             [model_name, storage]),
            # Match with model_name only (least specific)
            ("p.model_name = %s", [model_name]),
        ]

        for condition, values in conditions:
            # Skip conditions that don't have all required values
            if all(v is not None for v in values):
                query = f"""
                    SELECT p.model_name, p.price, p.category, m.name as manufacturer 
                    FROM products p 
                    JOIN manufacturers m ON p.manufacturer_id = m.id 
                    WHERE {condition} 
                    LIMIT 1
                """
                cursor.execute(query, tuple(values))
                product = cursor.fetchone()

                if product:
                    # Add a bit more detail and personalization to the response
                    responses = [
                        f"{product['manufacturer']} {product['model_name']} មានតម្លៃ {product['price']} ដុល្លារ។",
                        f"ខ្ញុំអាចបញ្ជាក់ថា {product['manufacturer']} {product['model_name']} មានតម្លៃ {product['price']} ដុល្លារ។",
                        f"តម្លៃបច្ចុប្បន្ននៃ {product['manufacturer']} {product['model_name']} គឺ {product['price']} ដុល្លារ។",
                        f"{product['manufacturer']} {product['model_name']} មានតម្លៃ {product['price']} ដុល្លារ។",
                    ]
                    dispatcher.utter_message(text=random.choice(responses))  # Send the response
                    cursor.close()
                    connection.close()
                    return []  # Stop at the first successful match

        # If no product is found
        dispatcher.utter_message(
            text= (
                f"ខ្ញុំសុំទោស ប៉ុន្តែខ្ញុំមិនអាចរកឃើញព័ត៌មានតម្លៃសម្រាប់ {model_name} ជាមួយនឹងលក្ខណៈបច្ចេកទេសទាំងនោះទេ។ សូមពិនិត្យមើលព័ត៌មានឡើងវិញហើយព្យាយាមម្តងទៀត។\n"
                f"🌐 ព័ត៌មានបន្ថែម៖ សូមមើលក្នុងគេហទំព័ររបស់យើង ` https://www.ecidisti.com/department/Electronics")
        )
        cursor.close()
        connection.close()
        return []