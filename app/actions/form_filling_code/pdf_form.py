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
        if question_meta_data['Type'] == 'input_text':
            return question_meta_data['form_feild']
        elif question_meta_data['Type'] == 'check_list':
            return question_meta_data['form_feild']
    
    def get_extra_question(self, question_meta_data):
        if question_meta_data['Type'] == 'input_text':
            return None
        elif question_meta_data['Type'] == 'check_list':
            return list(question_meta_data['form_feild'].keys())
    
    def fill_response(self, state_response, form_field, latest_message):
        if isinstance(form_field, dict):
            print("filling form_field", form_field)
            if isinstance(form_field[latest_message], list):
                for i in form_field[latest_message]:
                    state_response[i] = 'Yes'
            else:
                state_response[form_field] = 'Yes'
        elif isinstance(form_field, str):
            state_response[form_field] = latest_message
        return state_response

# Example usage
if __name__ == "__main__":
    pdf_path = '/home/amitshendgepro/rasa_bot/app/actions/form_feilds_NAVAR/Addendum Lease - K1384.pdf'
    output_path = "filled_form.pdf"