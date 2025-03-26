from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
from rasa_sdk.events import SlotSet
import random


def clear_all_slots():
    return [
        SlotSet("manufacturer", None),
        SlotSet("category", None),
        SlotSet("model_name", None),
        SlotSet("cpu", None),
        SlotSet("ram", None)
    ]

class ActionFetchProduct(Action):
    def name(self) -> str:
        return "action_fetch_product_by_name_kh"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        # ការចេញពីកម្រិតម៉ូឌែល
        model_name = tracker.get_slot("model_name")
        cpu = tracker.get_slot("cpu")
        ram = tracker.get_slot("ram")
        storage = tracker.get_slot("storage")

        connection = get_db_connection()
        if connection is None:
            dispatcher.utter_message(
                text="⚠️ សូមអភ័យទោស, ខ្ញុំមិនអាចចូលដំណើរការទិន្នន័យផលិតផលបានទេ។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ ឬទំនាក់ទំនងទៅកាន់ក្រុមគាំទ្ររបស់យើងសម្រាប់ជំនួយ។"
            )
            return []

        cursor = connection.cursor(dictionary=True)

        # កំណត់បញ្ជីលក្ខខណ្ឌដើម្បីសាកល្បង ប្រៀបធៀបការបញ្ចូលជាមួយកម្រិតទាំងអស់
        conditions = [
            # ស្រដៀងជាមួយ model_name, ram, cpu និង storage (មានសSpecificជាងគេ)
            ("p.model_name = %s AND p.ram = %s AND p.cpu = %s AND p.storage = %s",
             [model_name, ram, cpu, storage]),
            # ស្រដៀងជាមួយ model_name, ram និង cpu
            ("p.model_name = %s AND p.ram = %s AND p.cpu = %s",
             [model_name, ram, cpu]),
            # ស្រដៀងជាមួយ model_name, ram និង storage
            ("p.model_name = %s AND p.ram = %s AND p.storage = %s",
             [model_name, ram, storage]),
            # ស្រដៀងជាមួយ model_name, cpu និង storage
            ("p.model_name = %s AND p.cpu = %s AND p.storage = %s",
             [model_name, cpu, storage]),
            # ស្រដៀងជាមួយ model_name និង ram
            ("p.model_name = %s AND p.ram = %s",
             [model_name, ram]),
            # ស្រដៀងជាមួយ model_name និង cpu
            ("p.model_name = %s AND p.cpu = %s",
             [model_name, cpu]),
            # ស្រដៀងជាមួយ model_name និង storage
            ("p.model_name = %s AND p.storage = %s",
             [model_name, storage]),
            # ស្រដៀងជាមួយ model_name ប៉ុណ្ណោះ (មានតិចជាងគេ)
            ("p.model_name = %s", [model_name]),
        ]

        # បន្ថែមភាពចម្រុះទៅការណែនាំផលិតផល
        intros = [
            "បាទ/ចាស, នេះគឺជាផលិតផលមួយដែលស្របតាមតម្រូវការរបស់អ្នក៖",
            "ដោយផ្អែកលើការជ្រើសរើសរបស់អ្នក, ខ្ញុំស្នើសុំផលិតផលដូចតទៅ៖",
            "ខ្ញុំបានស្វែងរកផលិតផលមួយដែលសមនឹងតម្រូវការរបស់អ្នក៖",
            "ត្រឹមត្រូវ, នេះគឺជាជម្រើសល្អសម្រាប់អ្នក៖",
            "ផលិតផលនេះស្របតាមលក្ខណៈបញ្ជាក់របស់អ្នក៖",
            "ខ្ញុំស្នើសុំផលិតផលនេះផ្អែកលើលក្ខណៈកម្រិតរបស់អ្នក៖",
            "នេះគឺជាជម្រើសល្អសម្រាប់អ្នក៖",
            "ផលិតផលនេះអាចជារបស់ដែលអ្នកកំពុងស្វែងរកបានទេ៖",
        ]

        for condition, values in conditions:
            # ធ្វើបន្ទាន់ដើម្បីអត់បញ្ចូលដែលមិនមានតម្លៃទាំងអស់
            if all(v is not None for v in values):
                query = f"""
                    SELECT p.model_name, p.category, p.screen_size, p.screen, p.cpu, p.ram, p.storage, p.gpu, p.weight, p.price, m.name as manufacturer, i.image_url
                    FROM products p 
                    JOIN manufacturers m ON p.manufacturer_id = m.id
                    LEFT JOIN images i ON p.id = i.product_id
                    WHERE {condition} 
                    LIMIT 5
                """
                cursor.execute(query, tuple(values))
                products = cursor.fetchall()

                if products:
                    if len(products) == 1:
                        intro = random.choice(intros)  # រើសយកការណែនាំដោយចៃដន្យ
                        dispatcher.utter_message(text=intro)
                    else:
                        multi_intros = [
                            f"ខ្ញុំបានស្វែងរក {len(products)} ជម្រើសដែលស្របតាមតម្រូវការរបស់អ្នក៖",
                            f"នេះគឺជាផលិតផល {len(products)} ដែលផ្អែកលើតម្រូវការរបស់អ្នក៖",
                            f"ខ្ញុំបានស្វែងរក {len(products)} ផលិតផលដែលសមនឹងតម្រូវការរបស់អ្នក៖",
                            f"នេះគឺជាការណែនាំ {len(products)} ដែលស្របតាមការជ្រើសរើសរបស់អ្នក៖",
                            f"ខ្ញុំបានស្វែងរក {len(products)} ផលិតផលដែលសមនឹងលក្ខណៈបញ្ជាក់របស់អ្នក៖",
                        ]
                        intro = random.choice(multi_intros)  # រើសយកការណែនាំនៃជម្រើសមួយ
                        dispatcher.utter_message(text=intro)

                    for product in products:
                        # បង្ហាញរូបភាពប្រសិនបើមាន
                        if product['image_url']:
                            dispatcher.utter_message(image=product['image_url'])

                        dispatcher.utter_message(
                            text=f"■ {product['manufacturer']} {product['model_name']}\n"
                                 f"○ Category: {product['category']}\n"
                                 f"○ Price: ${product['price']}\n"
                                 f"○ Display: {product['screen_size']}\" {product['screen']}\n"
                                 f"○ Performance: {product['cpu']}, {product['ram']} RAM\n"
                                 f"○ Storage: {product['storage']}\n"
                                 f"○ Graphics: {product['gpu']}\n"
                                 f"○ Weight: {product['weight']} kg\n"
                                 f"🌐 ព័ត៌មានបន្ថែម: ទៅកាន់គេហទំព័ររបស់យើង` https://www.ecidisti.com/department/Electronics"
                        )
                    cursor.close()
                    connection.close()
                    return []

        dispatcher.utter_message(
            text="❌ សូមអភ័យទោស, ខ្ញុំមិនអាចស្វែងរកផលិតផលដែលស្របតាមលក្ខខណ្ឌរបស់អ្នកបានទេ។ សូមពិចារណាអំពីការកែតម្រូវលក្ខខណ្ឌស្វែងរករបស់អ្នក ឬទំនាក់ទំនងទៅកាន់ក្រុមគាំទ្ររបស់យើងសម្រាប់ជំនួយបន្ថែម។"
        )
        cursor.close()
        connection.close()
        return clear_all_slots()
