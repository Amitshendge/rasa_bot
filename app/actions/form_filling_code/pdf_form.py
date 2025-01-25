import json
from fillpdf import fillpdfs
import os
import base64

class PDFFormFiller:
    def __init__(self):
        pass


    def generate_download_link(self, file_path, link_text="Download File"):
        """
        Generates a hyperlink to download any file.
        
        Parameters:
        - file_path: Path to the file.
        - link_text: Text to display for the download link.
        
        Returns:
        - str: HTML link for downloading the file.
        """
        try:
            with open(file_path, "rb") as file:
                file_bytes = file.read()
                file_name = file_path.split("/")[-1]  # Extract file name from path
                mime_type = "application/octet-stream"  # Generic MIME type for files
                b64_file = base64.b64encode(file_bytes).decode()  # Encode file to Base64
                href = f'<a href="data:{mime_type};base64,{b64_file}" download="{file_name}">{link_text}</a>'
                print("href", href)
                return href
        except Exception as e:
            return f"Error generating download link: {e}"
        
    def fill_pdf(self, pdf_path, output_path, feild_values):
        print("MMMM")
        fillpdfs.write_fillable_pdf(pdf_path, output_path, feild_values)
        print("MMMM")
        fillpdfs.flatten_pdf(output_path, output_path.replace(os.path.basename(output_path), "flatten_"+os.path.basename(output_path)))
        print("GGGG")
        return self.generate_download_link(output_path)
    
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

    def autofill_question(self, state, question_meta_data):
        if question_meta_data['autofill_type'] == 'static':
            self.fill_response(state, question_meta_data['form_feild'], None, question_meta_data['autofill_value'])
            # state["responses"][question_meta_data['form_feild']] = question_meta_data['autofill_value']
        elif question_meta_data['autofill_type'] == 'reference':
            self.fill_response(state, question_meta_data['form_feild'], None, state["responses"][question_meta_data['autofill_value']])
            # state["responses"][question_meta_data['form_feild']] = state["responses"][question_meta_data['autofill_value']]
        return state

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