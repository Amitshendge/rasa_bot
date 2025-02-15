import json
from fillpdf import fillpdfs
import os
import base64
import sqlite3
import datetime

class PDFFormFiller:
    def __init__(self):
        self.static_maping = self.read_json_form('/app/actions/form_filling_code/autofill_static_mapping.json')
        self.user_maping = self.read_json_form('/app/actions/form_filling_code/autofill_user_mapping.json')
        self.user_data = self.sqlite_query('/app/actions/form_filling_code/real_estate_onboarding.db', 'onboarding', 'bimal@onest.realestate')
    
    def sqlite_query(self, db_path, table_name, email):
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Execute query to fetch user data
            cursor.execute(f"SELECT * FROM {table_name} WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to dictionary
            user_info = dict(zip(column_names, row)) if row else None
            return user_info
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def read_json_form(self, file_path):
        with open(file_path, "r") as file:
            main_json = json.load(file)
            main_json['last_question'] = {"Type":"LAST"}
        return main_json

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
        elif question_meta_data['Type'] == 'check_list_form':
            if 'next_action' in question_meta_data:
                add_questions = question_meta_data['next_action']
            return None, add_questions
    
    def get_extra_question(self, question_meta_data):
        if question_meta_data['Type'] == 'input_text':
            return None
        elif question_meta_data['Type'] == 'check_list':
            return list(question_meta_data['form_feild'].keys())
        elif question_meta_data['Type'] == 'check_list_form':
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
        elif question_meta_data['autofill_type'] == 'static_mapping':
            self.fill_response(state, question_meta_data['form_feild'], None, self.static_maping[question_meta_data['autofill_value']])
        elif question_meta_data['autofill_type'] == 'user_mapping':
            self.fill_response(state, question_meta_data['form_feild'], None, self.user_data[question_meta_data['autofill_value']])
        elif question_meta_data['autofill_type'] == 'date_today':
            self.fill_response(state, question_meta_data['form_feild'], None, datetime.datetime.now().strftime("%d-%m-%Y"))
        elif question_meta_data['autofill_type'] == 'date_offset':
            self.fill_response(state, question_meta_data['form_feild'], None, (datetime.datetime.now() + datetime.timedelta(days=question_meta_data['autofill_value'])).strftime("%d-%m-%Y"))
        return state

    def fill_response(self, state, form_field, add_questions, latest_message):
        form_name_change = None
        if isinstance(form_field, dict):
            if isinstance(form_field[latest_message], list):
                for i in form_field[latest_message]:
                    if i != 'NA' or i != '':
                        state["responses"][i] = 'Yes'
            else:
                if i != 'NA' or i != '':
                    state["responses"][form_field] = 'Yes'
            if add_questions:
                try:
                    print(add_questions[latest_message])
                    state["questions"] = self.insert_into_dict(state["questions"], add_questions[latest_message], state["current_index"]) 
                except:
                    pass
            print("state", state)
        elif isinstance(form_field, str):
            state["responses"][form_field] = latest_message
        elif form_field == None:
            add_questions = add_questions[latest_message]
            if add_questions:
                print("add_questions", add_questions)
                if add_questions:
                    if 'question' in add_questions:
                        state["questions"] = self.insert_into_dict(state["questions"], add_questions['question'], state["current_index"])
                    elif 'form':
                        form_name_change = add_questions['form']
                        state["questions"] = self.insert_into_dict(state["questions"], self.read_json_form(f"/app/actions/form_feilds_mapping_v2/{form_name_change}.json"), state["current_index"])
                    print("state", state)
            else:
                pass
        return state, form_name_change