from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import random


class ActionList(Action):
    def name(self) -> Text:
        return "action_list_kh"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT m.name, GROUP_CONCAT(DISTINCT p.category SEPARATOR ' - ') "
                "FROM manufacturers m "
                "LEFT JOIN products p ON m.id = p.manufacturer_id "
                "GROUP BY m.name"
            )
            results = cursor.fetchall()
            connection.close()

            if results:
                intro_messages = [
                    "នេះគឺជាបញ្ជីពេញលេញនៃម៉ាកផលិតផលនិងប្រភេទផលិតផលដែលទាក់ទង៖",
                    "ខាងក្រោមគឺជាម៉ាកនិងប្រភេទផលិតផល៖",
                    "នៅខាងក្រោម អ្នកនឹងរកឃើញម៉ាកនិងប្រភេទផលិតផល៖",
                    "នេះគឺជារបាយការណ៍សង្ខេបនៃម៉ាកផលិតផលនិងប្រភេទផលិតផលដែលយើងមាន:",
                    "នេះគឺជាម៉ាកផលិតផលនិងប្រភេទផលិតផលដែលយើងផ្តល់ជូន:",
                    "បញ្ជីខាងក្រោមបង្ហាញពីម៉ាកផលិតផលនិងប្រភេទផលិតផលដែលយើងមាន៖",
                ]

                manufacturers_list = "\n".join(
                    [f"🔹 {manufacturer}: {categories if categories else 'មិនមានផលិតផល'}" for
                     manufacturer, categories in results])

                # Construct the response only once
                response = f"{random.choice(intro_messages)}\n{manufacturers_list}"
                dispatcher.utter_message(
                    text=(
                        f"{response}\nតើអ្នកចង់ដឹងបន្ថែមអំពីផលិតផលទេ?")
                )
            else:
                dispatcher.utter_message(
                    text="ខ្ញុំបានពិនិត្យហើយ តែខ្ញុំមិនអាចរកឃើញម៉ាកផលិតផលនៅក្នុងទិន្នន័យទេ។ សូមប្រាប់ខ្ញុំប្រសិនបើអ្នកត្រូវការជំនួយអ្វីផ្សេងទៀត ឬអ្នកអាចពិនិត្យតំណភ្ជាប់នៃគេហទំព័ររបស់យើងខាងក្រោម!\n"
                         f"🌐 ព័ត៌មានបន្ថែម: សូមចូលទៅកាន់គេហទំព័ររបស់យើង https://www.ecidisti.com/department/Electronics")
        except Exception as e:
            dispatcher.utter_message(
                text="អូរ! មានបញ្ហា​ខ្លះនៅពេលដែលខ្ញុំកំពុងស្វែងរកម៉ាកផលិតផល។ សូមព្យាយាមម្តងទៀតក្នុងរយៈពេលខ្លី!")

        return []
