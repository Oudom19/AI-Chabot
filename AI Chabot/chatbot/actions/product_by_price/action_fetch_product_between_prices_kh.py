from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet  # Import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import random


class ActionFetchProductBetweenPrices(Action):
    def name(self) -> str:
        return "action_fetch_product_between_prices_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> List[Dict[Text, Any]]:
        # Define intro message templates in Khmer
        PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "នេះគឺជាប្រភេទផលិតផល {manufacturer} និង {category} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}។ ៖",
            "ខ្ញុំបានរកឃើញផលិតផលល្អៗពី {manufacturer} និង {category} ដែលមានតម្លៃចន្លោះ ${min_price:.2f} និង ${max_price:.2f}:",
            "សូមពិនិត្យផលិតផល {manufacturer} និង {category} ទាំងនេះដែលមានតម្លៃចន្លោះ ${min_price:.2f} និង ${max_price:.2f}:",
            "នេះគឺជាជម្រើសផលិតផល {manufacturer} និង {category} ដែលមានតម្លៃនៅចន្លោះ {min_price:.2f} និង {max_price:.2f}:",
            "នេះគឺជាផលិតផលល្អៗពី {manufacturer} និង {category} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "នេះគឺជាប្រភេទផលិតផល {manufacturer} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}។ ៖",
            "ខ្ញុំបានរកឃើញផលិតផលល្អៗពី {manufacturer} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:",
            "សូមពិនិត្យផលិតផល {manufacturer} ទាំងនេះដែលមានតម្លៃចន្លោះ ${min_price:.2f} និង ${max_price:.2f}:",
            "នេះគឺជាជម្រើសផលិតផល {manufacturer} ដែលមានតម្លៃនៅចន្លោះ {min_price:.2f} និង {max_price:.2f}:",
            "នេះគឺជាផលិតផលល្អៗពី {manufacturer} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "នេះគឺជាប្រភេទផលិតផល {category} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}។ ៖",
            "ខ្ញុំបានរកឃើញផលិតផលល្អៗពី {category} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:",
            "សូមពិនិត្យផលិតផល {category} ទាំងនេះដែលមានតម្លៃចន្លោះ ${min_price:.2f} និង ${max_price:.2f}:",
            "នេះគឺជាជម្រើសផលិតផល {category} ដែលមានតម្លៃនៅចន្លោះ {min_price:.2f} និង {max_price:.2f}:",
            "នេះគឺជាផលិតផលល្អៗពី {category} ដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:"
        ]

        PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "នេះគឺជាប្រភេទផលិតផលល្អៗដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}។ សូមពិនិត្យវា៖",
            "ខ្ញុំបានរកឃើញជម្រើសល្អៗក្នុងថ្លៃចន្លោះ ${min_price:.2f} ដល់ ${max_price:.2f}:",
            "សូមពិនិត្យផលិតផលទាំងនេះដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}:",
            "នេះគឺជាជម្រើសផលិតផលក្នុងថ្លៃចន្លោះ ${min_price:.2f} ទៅ ${max_price:.2f}:",
            "នេះគឺជាផលិតផលល្អៗក្នុងថ្លៃ ${min_price:.2f} ដល់ ${max_price:.2f}:"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS = [
            "សូមអភ័យទោស គ្មានផលិតផល {manufacturer} និង {category} ដែលមានតម្លៃនៅចន្លោះ ${min_price:.2f} និង ${max_price:.2f}។ តើអ្នកចង់កែប្រែតម្លៃរបស់អ្នកទេ?",
            "មិនមានផលិតផល {manufacturer} និង {category} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f}។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "ខ្ញុំមិនបានរកឃើញផលិតផល {manufacturer} និង {category} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f} ទេ។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "គ្មានផលិតផល {manufacturer} និង {category} តាមតម្លៃនេះទេ។ តើអ្នកចង់កែតម្លៃរបស់អ្នកទេ?"
        ]

        NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS = [
            "សូមអភ័យទោស គ្មានផលិតផល {manufacturer} ដែលមានតម្លៃនៅចន្លោះ ${min_price:.2f} និង ${max_price:.2f}។ តើអ្នកចង់កែប្រែតម្លៃរបស់អ្នកទេ?",
            "មិនមានផលិតផល {manufacturer} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f}។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "ខ្ញុំមិនបានរកឃើញផលិតផល {manufacturer} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f} ទេ។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "គ្មានផលិតផល {manufacturer} តាមតម្លៃនេះទេ។ តើអ្នកចង់កែតម្លៃរបស់អ្នកទេ?"
        ]

        NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS = [
            "សូមអភ័យទោស គ្មានផលិតផល {category} ដែលមានតម្លៃនៅចន្លោះ ${min_price:.2f} និង ${max_price:.2f}។ តើអ្នកចង់កែប្រែតម្លៃរបស់អ្នកទេ?",
            "មិនមានផលិតផល {category} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f}។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "ខ្ញុំមិនបានរកឃើញផលិតផល {category} នៅក្នុងតម្លៃ ${min_price:.2f} - ${max_price:.2f} ទេ។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?",
            "គ្មានផលិតផល {category} តាមតម្លៃនេះទេ។ តើអ្នកចង់កែតម្លៃរបស់អ្នកទេ?"
        ]

        NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS = [
            "សូមអភ័យទោស គ្មានផលិតផលដែលមានតម្លៃរវាង ${min_price:.2f} និង ${max_price:.2f}។ តើអ្នកចង់ព្យាយាមកែប្រែតម្លៃទេ?",
            "គ្មានជម្រើសនៅក្នុងតម្លៃ ${min_price:.2f} ដល់ ${max_price:.2f} ទេ។ តើអ្នកចង់កំណត់បច្ចុប្បន្នភាព?",
            "យើងមិនមានផលិតផលដែលមានតម្លៃនៅចន្លោះ ${min_price:.2f} និង ${max_price:.2f} ទេ។ តើអ្នកចង់កែការជ្រើសរើស?",
            "គ្មានផលិតផលនៅក្នុងតម្លៃ ${min_price:.2f} ដល់ ${max_price:.2f} ទេ។ តើអ្នកចង់ព្យាយាមតម្លៃផ្សេងទៀតទេ?"
        ]

        # Get slots
        min_price = tracker.get_slot("min_price")
        max_price = tracker.get_slot("max_price")
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        # Validate price range
        if not min_price or not max_price:
            dispatcher.utter_message(
                text="ខ្ញុំនៅតែរីករាយក្នុងការស្វែងរកផលិតផលនៅក្នុងថ្លៃដែលអ្នកបានបញ្ជាក់។ តើអ្នកអាចផ្តល់តម្លៃអប្បបរមា និងខ្ពស់បំផុតបានទេ?"
            )
            return []

        try:
            min_price = float(min_price)  # Convert min_price to float
            max_price = float(max_price)  # Convert max_price to float
        except ValueError:
            dispatcher.utter_message(
                text="សូមអភ័យទោស ប៉ុន្តែខ្ញុំមិនអាចយល់ពីតម្លៃដែលអ្នកបានបញ្ជាក់។ តើអ្នកអាចផ្តល់តម្លៃជាទាំងស្រុងបានទេ?"
            )
            return []

        # Get database connection
        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="ខ្ញុំមិនអាចចូលប្រើមូលដ្ឋានទិន្នន័យផលិតផលនៅពេលនេះទេ។ សូមព្យាយាមម្ដងទៀតនៅពេលក្រោយ ឬទំនាក់ទំនងជួយសូមបំរែបំរួល។"
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
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category,
                                                          min_price=min_price, max_price=max_price)
                elif manufacturer:
                    intro_template = random.choice(PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, min_price=min_price,
                                                          max_price=max_price)
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
                    text=(
                        "គំរូដ៏ល្អទាំងនេះផ្តល់នូវលក្ខណៈពិសេស និងការអនុវត្តដ៏ល្អ។ សូមប្រាប់ខ្ញុំប្រសិនបើអ្នកចង់ដឹងបន្ថែមអំពីជម្រើសណាមួយ។\n"
                        f"🌐 ព័ត៌មានបន្ថែម៖ សូមមើលក្នុងគេហទំព័ររបស់យើង ` https://www.ecidisti.com/department/Electronics"
                    )
                )
            else:
                # Determine which no-products-found intro template to use
                if manufacturer and category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_AND_CATEGORY_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, category=category,
                                                          min_price=min_price, max_price=max_price)
                elif manufacturer:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_MANUFACTURER_INTROS)
                    intro_message = intro_template.format(manufacturer=manufacturer, min_price=min_price,
                                                          max_price=max_price)
                elif category:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITH_CATEGORY_INTROS)
                    intro_message = intro_template.format(category=category, min_price=min_price, max_price=max_price)
                else:
                    intro_template = random.choice(NO_PRODUCTS_FOUND_WITHOUT_MANUFACTURER_OR_CATEGORY_INTROS)
                    intro_message = intro_template.format(min_price=min_price, max_price=max_price)

                dispatcher.utter_message(text=intro_message)

        except Exception as e:
            dispatcher.utter_message(
                text="សូមអភ័យទោស ប៉ុន្តែមានបញ្ហាក្នុងការទាញយកផលិតផល។ សូមព្យាយាមម្ដងទៀត។"
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
