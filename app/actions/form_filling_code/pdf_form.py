import json
from fillpdf import fillpdfs
import os

class PDFFormFiller:
    def __init__(self):
        pass

    def fill_pdf(self, pdf_path, output_path, feild_values):
        fillpdfs.write_fillable_pdf(pdf_path, output_path, feild_values)
        fillpdfs.flatten_pdf(output_path, output_path.replace(os.path.basename(output_path), "flatten_"+os.path.basename(output_path)))

    def get_form_feild(self, question_meta_data):
        add_questions = None
        if question_meta_data['Type'] == 'input_text':
            return question_meta_data['form_feild'], add_questions
        elif question_meta_data['Type'] == 'check_list':
            if 'questions' in question_meta_data:
                add_questions = question_meta_data['questions']
            return question_meta_data['form_feild'], add_questions
    
    def get_extra_question(self, question_meta_data):
        if question_meta_data['Type'] == 'input_text':
            return None
        elif question_meta_data['Type'] == 'check_list':
            return list(question_meta_data['form_feild'].keys())
    
    def insert_into_dict(self, original_dict, new_entries, index):
        items = list(original_dict.items())
        new_items = list(new_entries.items())
        items[index:index] = new_items
        print("items", items)
        return dict(items)

    def fill_response(self, state, form_field, add_questions, latest_message):
        if isinstance(form_field, dict):
            if isinstance(form_field[latest_message], list):
                for i in form_field[latest_message]:
                    state["responses"][i] = 'Yes'
            else:
                state["responses"][form_field] = 'Yes'
            if add_questions:
                print(add_questions[latest_message])
                state["questions"] = self.insert_into_dict(state["questions"], add_questions[latest_message], state["current_index"]) 
            print("state", state)
        elif isinstance(form_field, str):
            state["responses"][form_field] = latest_message
        return state

# Example usage
if __name__ == "__main__":
    pdf_path = '/home/amitshendgepro/rasa_bot/app/actions/form_feilds_NAVAR/Addendum Lease - K1384.pdf'
    output_path = "filled_form.pdf"