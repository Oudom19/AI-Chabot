from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ..actions import get_db_connection
import random


class ActionList(Action):
    def name(self) -> Text:
        return "action_list"

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
                    "Here is a comprehensive list of manufacturers and the associated product categories:",
                    "The following are the manufacturers and the types of products:",
                    "Below, you will find the manufacturers along with the product categories:",
                    "Here is a summary of manufacturers and the respective product categories we specialize in:",
                    "Find below the list of manufacturers and the product categories available through them:",
                    "The following manufacturers and their respective product categories are available for your review:",
                    "Here is an overview of manufacturers and the range of product categories we offer:",
                    "The list below highlights manufacturers and the types of products we supply:",
                    "Please review the manufacturers and the specific product categories we cover:",
                    "Here’s a detailed breakdown of manufacturers and the categories of products we offer:",
                ]

                manufacturers_list = "\n".join(
                    [f"🔹 {manufacturer}: {categories if categories else 'No category available'}" for
                     manufacturer, categories in results])

                # Construct the response only once
                response = f"{random.choice(intro_messages)}\n{manufacturers_list}"
                dispatcher.utter_message(
                    text=(
                        f"{response}\nWould you like to know more about the products?")
                )
            else:
                dispatcher.utter_message(
                    text="I checked, but I couldn't find any manufacturers in the database. Let me know if you need help with something else or you can check the link of our website below!\n"
                          f"🌐 More Info: Visit our website https://www.ecidisti.com/department/Electronics")
        except Exception as e:
            dispatcher.utter_message(
                text="Oops! Something went wrong while fetching the manufacturers. Try again in a moment!")

        return []