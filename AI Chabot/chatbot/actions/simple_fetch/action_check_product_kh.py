import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
from rasa_sdk.events import SlotSet

def clear_all_slots():
    return [
        SlotSet("manufacturer", None),
        SlotSet("category", None),
        SlotSet("model_name", None),
        SlotSet("cpu", None),
        SlotSet("ram", None)
    ]

# Helper function for database connection
def execute_query(query, params):
    connection = get_db_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()

# Response intros
INTRO_MESSAGES = [
    "យល់ហើយ! នេះគឺជាព័ត៌មានដែលខ្ញុំបានស្វែងរក:",
    "ប្រាកដណាស់! នេះគឺជាព័ត៌មានដែលអ្នកបានស្នើ:",
    "ប្រាកដណាស់! នេះគឺជាព័ត៌មានដែលមាន:",
    "បាទ! នេះគឺជាព័ត៌មានដែលយើងមាន:",
    "បាទ! អនុញ្ញាតឲ្យខ្ញុំបង្ហាញព័ត៌មានសម្រាប់អ្នក:"
]

# ---- Class 1: Handling Manufacturer + Category Query ----
class ActionCheckManufacturerCategory(Action):
    def name(self) -> Text:
        return "action_check_manufacturer_category_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        manufacturer = tracker.get_slot("manufacturer")
        category = tracker.get_slot("category")

        if not manufacturer or not category:
            dispatcher.utter_message(text="សូមបញ្ជាក់ពីឈ្មោះផលិតផល។")
            return clear_all_slots()

        query = """
            SELECT p.model_name 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(m.name) = LOWER(%s) AND LOWER(p.category) = LOWER(%s)
        """
        models = execute_query(query, (manufacturer.lower(), category.lower()))

        if models:
            model_list = ", ".join([model["model_name"] for model in models])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" {manufacturer} ផ្តល់ជូនម៉ូដលខាងក្រោមក្នុងប្រភេទ {category}: {model_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "តើអ្នកសង្ឃឹមថា ម៉ូដលនិងប្រភេទទាំងនេះគឺជាទំនិញដែលអ្នកកំពុងស្វែងរកទេ?",
                "តើអ្នកចង់មើលផលិតផលបន្ថែមពីអ្នកផលិតនិងប្រភេទទាំងនេះទេ?",
                "តើអ្នកចង់ស្វែងរកអ្នកផលិតឬប្រភេទផ្សេងទៀតទេ?",
                "តើអ្នកចង់ពិនិត្យប៉ុណ្ណោះនៃម៉ាកឬប្រភេទផលិតផលទេ?",
                "តើអ្នកចង់បានយោបល់សម្រាប់ម៉ាកឬប្រភេទដែលស្រដៀងគ្នាទេ?",
                "តើអ្នកត្រូវការជំនួយក្នុងការស្វែងរកជម្រើសផ្សេងទៀតពីអ្នកផលិតទាំងនេះឬក្នុងប្រភេទនេះទេ?",
                "តើអ្នកចង់ពិនិត្យម៉ាកនិងប្រភេទទាំងនេះទៀតទេ?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"សូមអភ័យទោស ប៉ុន្តែយើងមិនមានផលិតផល {category} ពី {manufacturer} នៅពេលនេះទេ។")

        return clear_all_slots()

# ---- Class 2: Handling Manufacturer Query ----
class ActionCheckManufacturer(Action):
    def name(self) -> Text:
        return "action_check_manufacturer_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        manufacturer = tracker.get_slot("manufacturer")

        if not manufacturer:
            dispatcher.utter_message(text="សូមបញ្ជាក់ពីឈ្មោះម៉ាក ឬប្រ៊ែនម្តងទៀត។")
            return clear_all_slots()

        query = """
            SELECT DISTINCT p.category 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(m.name) = LOWER(%s)
        """
        categories = execute_query(query, (manufacturer.lower(),))

        if categories:
            category_list = ", ".join([cat["category"] for cat in categories])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" {manufacturer} មានផលិតផលនៅក្នុងប្រភេទដូចខាងក្រោម: {category_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "តើនេះគឺជាផលិតផលដែលអ្នកកំពុងស្វែងរកទេ?",
                "តើអ្នកចង់បានព័ត៌មានលម្អិតពីផលិតផលណាមួយទេ?",
                "តើមានផលិតផលណាមួយដែលផ្គូរផ្គងនឹងតម្រូវការរបស់អ្នកទេ?",
                "តើអ្នកចង់មើលផលិតផលជាច្រើននៅក្នុងប្រភេទនេះទេ?",
                "តើអ្នកត្រូវការព័ត៌មានស្តីពីលក្ខណៈបច្ចេកវិទ្យា ឬតម្លៃពីផលិតផលណាមួយទេ?",
                "តើអ្នកចង់ស្វែងរកជម្រើសផ្សេងទៀតពីអ្នកផលិតនេះទេ?",
                "តើអ្នកចង់បានយោបល់សម្រាប់ផលិតផលផ្សេងទៀតដែលអាចត្រូវការអ្នកទេ?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"សូមអភ័យទោស ប៉ុន្តែយើងមិនមានផលិតផលពី {manufacturer} នៅពេលនេះទេ។")

        return clear_all_slots()

# ---- Class 3: Handling Category Query ----
class ActionCheckCategory(Action):
    def name(self) -> Text:
        return "action_check_category_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("category")

        if not category:
            dispatcher.utter_message(text="សូមបញ្ជាក់ពីប្រភេទផលិតផល។")
            return clear_all_slots()

        query = """
            SELECT DISTINCT m.name as manufacturer 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(p.category) = LOWER(%s)
        """
        manufacturers = execute_query(query, (category.lower(),))

        if manufacturers:
            manu_list = ", ".join([manu["manufacturer"] for manu in manufacturers])
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + f" យើងមានផលិតផល {category} ពី {manu_list}.")
            # Follow-up question (only one)
            follow_up_questions = [
                "តើប្រភេទនេះមានអ្វីដែលអ្នកកំពុងស្វែងរកទេ?",
                "តើអ្នកចង់ស្វែងរកផលិតផលបន្ថែមនៅក្នុងប្រភេទនេះទេ?",
                "តើអ្នកចង់មើលជម្រើសផ្សេងទៀតពីប្រភេទនេះទេ?",
                "តើប្រភេទនេះផ្គូរផ្គងនឹងតម្រូវការរបស់អ្នកទេ? ឬតើអ្នកចង់ពិនិត្យប្រភេទផ្សេងទៀតទេ?",
                "តើអ្នកកំពុងស្វែងរកផលិតផលប្រភេទផ្សេងទៀតទេ?",
                "តើអ្នកចង់បានស្នើសុំជម្រើសផ្សេងទៀតសម្រាប់ប្រភេទផ្សេងទៀតទេ?",
                "តើអ្នកត្រូវការព័ត៌មានលម្អិតពីផលិតផលក្នុងប្រភេទនេះទេ?",
                "តើអ្នកចង់ស្វែងរកប្រភេទផ្សេងទៀតដែលទាក់ទង?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"សូមអភ័យទោស ប៉ុន្តែយើងមិនមានផលិតផល {category} នៅពេលនេះទេ។")

        return clear_all_slots()

# ---- Class 4: Handling Model Name Query ----
class ActionCheckModel(Action):
    def name(self) -> Text:
        return "action_check_model_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        model_name = tracker.get_slot("model_name")

        if not model_name:
            dispatcher.utter_message(text="សូមបញ្ជាក់ពីឈ្មោះម៉ូដែល។")
            return clear_all_slots()

        query = """
            SELECT p.model_name, p.price, p.category, p.cpu, p.ram, p.storage, m.name as manufacturer 
            FROM products p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE LOWER(p.model_name) = LOWER(%s) 
        """
        products = execute_query(query, (model_name.lower(),))

        if products:
            dispatcher.utter_message(text=random.choice(INTRO_MESSAGES) + "\n")
            for product in products:
                dispatcher.utter_message(
                    text=(
                        f"■ {product['model_name']}\n"
                        f"● អ្នកផលិត: {product['manufacturer']}\n"
                        f"● តម្លៃ: ${product['price']:.2f}\n"
                        f"● ប្រភេទ: {product['category']}\n"
                        f"● CPU: {product['cpu']}\n"
                        f"● RAM: {product['ram']}\n"
                        f"● សារពើភ័ណ្ឌ: {product['storage']}\n"
                    )
                )
            # Follow-up question (only one)
            follow_up_questions = [
                "តើនេះគឺជាផលិតផលដែលអ្នកកំពុងស្វែងរកទេ?",
                "តើអ្នកចង់បានព័ត៌មានលម្អិតពីផលិតផលណាមួយទេ?",
                "តើមានផលិតផលណាមួយដែលផ្គូរផ្គងនឹងតម្រូវការរបស់អ្នកទេ?",
                "តើអ្នកចង់មើលផលិតផលបន្ថែមដូចនេះទេ?",
                "តើអ្នកត្រូវការព័ត៌មានបន្ថែមពីផលិតផលណាមួយទេ?",
                "តើអ្នកចង់ស្វែងរកជម្រើសផលិតផលផ្សេងទៀតទេ?",
                "តើអ្នកមានចំណាប់អារម្មណ៍លើផលិតផលស្រដៀងដែលមានបញ្ជាក់ផ្សេងទៀតទេ?",
                "តើអ្នកចង់បានស្នើសុំជម្រើសផ្សេងទៀតសម្រាប់ផលិតផលដែលអាចឆាប់ប្រើបានទេ?"
            ]
            dispatcher.utter_message(text=random.choice(follow_up_questions))
        else:
            dispatcher.utter_message(text=f"សូមអភ័យទោស ប៉ុន្តែខ្ញុំមិនអាចស្វែងរកព័ត៌មានសម្រាប់ {model_name} ได้ទេ។")

        return clear_all_slots()
