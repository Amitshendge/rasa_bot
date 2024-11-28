import json
from fillpdf import fillpdfs
import os

class PDFFormFiller:
    def __init__(self):
        pass

    def fill_pdf(self, pdf_path, output_path, feild_values):
        fillpdfs.write_fillable_pdf(pdf_path, output_path, feild_values)
        fillpdfs.flatten_pdf(output_path, output_path.replace(os.path.basename(output_path), "flatten_"+os.path.basename(output_path)))

# Example usage
if __name__ == "__main__":
    pdf_path = '/home/amitshendgepro/rasa_bot/app/actions/form_feilds_NAVAR/Addendum Lease - K1384.pdf'
    output_path = "filled_form.pdf"