# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop, AllSlotsReset
import json
import os
import difflib

class ActionAskDynamicQuestions(Action):
    def name(self) -> str:
        return "action_ask_dynamic_questions"

    def read_json(self, file_path):
        with open(file_path, "r") as file:
            return json.load(file)
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Path to the JSON file to store state
        form_name_final = tracker.get_slot("identified_form_name")
        print(tracker.get_slot("response_list"))
        print("form_name_final", form_name_final)
        response_list = tracker.get_slot("response_list")
        if response_list:
            state = response_list[0]
        else:
            state = {
                "questions": self.read_json(f"/app/actions/form_feilds_mapping/{form_name_final}.json"),
                "current_index": 0,
                "responses": {}
            }
        print("state", state)
        # Get current index and questions
        current_index = state["current_index"]
        questions = list(state["questions"].keys())

        # Save the user's latest response if it's not the initial call
        if tracker.latest_message.get("text") and current_index > 0:
            # Append the latest response to the responses list
            state["responses"][state['questions'][questions[current_index-1]]] = tracker.latest_message["text"]
        # Check if there are more questions to ask
        if current_index < len(questions):
            # Ask the next question
            next_question = questions[current_index]
            dispatcher.utter_message(text=next_question)
            # Increment the current index
            state["current_index"] += 1
            # Save the updated state back to the JSON file
            print("state", state)
            return [ActiveLoop('action_ask_dynamic_questions'), SlotSet("response_list", state)]
        else:
            print("Else")
            print("state", state)
            # All questions have been asked
            from actions.form_filling_code.pdf_form import PDFFormFiller
            pdf_path = f'/app/actions/form_feilds_NAVAR/{form_name_final}.pdf'
            output_path = f"/app/outputs/{form_name_final}_filled.pdf"
            feild_values = state["responses"]
            PDFFormFiller().fill_pdf(pdf_path, output_path, feild_values)
            dispatcher.utter_message(text="Thank you for answering all the questions!")
            dispatcher.utter_message(json_message=f"{form_name_final}_filled.pdf")
            return [ActiveLoop(None),AllSlotsReset()]


class SayFormName(Action):
    def name(self) -> Text:
        return "say_form_name"

    def find_closest_form(self, user_input, form_names):
        """
        Matches the user's input to the closest form name in the list.
        
        :param user_input: String input from the user.
        :param form_names: List of form names to match against.
        :return: Closest form name.
        """
        print("user_input", user_input)
        print("form_names", form_names)
        closest_match = difflib.get_close_matches(user_input, form_names, n=1, cutoff=0.1)
        return closest_match[0] if closest_match else None
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("form", tracker.slots)
        form_name = tracker.get_slot("form_name2")
        if form_name:
            final_form_name = self.find_closest_form(form_name, [i[:-4] for i in list(os.listdir("/app/actions/form_feilds_NAVAR"))])
            print(tracker.get_slot("identified_form_name"))
            dispatcher.utter_message(text=f"Do you want to fill {final_form_name}")
        else:
            dispatcher.utter_message(text="I don't know which form you're filling out!")
        
        return [SlotSet("identified_form_name", final_form_name)]
    
class All_reset(Action):
    def name(self) -> Text:
        return "all_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]