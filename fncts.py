import os
import cv2
from paddleocr import PPStructure,draw_structure_result,save_structure_res
from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
from datetime import datetime
import json
import pandas as pd

# Function to convert Excel file to JSON
def excel_to_json(excel_file_path):
    # Read Excel file
    df = pd.read_excel(excel_file_path)
    
    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records')
    return json_data

def tblrec(img_path, save_folder= './output', lang='en'):
    # English image
    table_engine = PPStructure(layout=False, show_log=True, lang=lang)

    img = cv2.imread(img_path)
    result = table_engine(img)
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H%M%S")
    save_structure_res(result, save_folder, os.path.basename(formatted_datetime))

    print('saved at:', save_folder+formatted_datetime)
    
    # Directory where Excel files are stored
    directory = save_folder+'/'+formatted_datetime

    # List files in the directory
    files = os.listdir(directory)

    # Find the first .xlsx file
    xlsx_files = [file for file in files if file.endswith('.xlsx')]

    if xlsx_files:
        # Get the first .xlsx file
        first_xlsx_file = os.path.join(directory, xlsx_files[0])
        
        # Convert Excel to JSON
        json_data = excel_to_json(first_xlsx_file)
        
        # Rename Excel file to 'extracted.xlsx'
        # new_xlsx_file = os.path.join(directory, 'extracted.xlsx')
        # os.rename(first_xlsx_file, new_xlsx_file)
    
        # Write JSON data to a file
        json_output_file = os.path.splitext(first_xlsx_file)[0] + '.json'
        with open(json_output_file, 'w') as json_file:
            json_file.write(json_data)
        
        print(f"Excel file '{first_xlsx_file}' converted to JSON: '{json_output_file}'")
        return first_xlsx_file 
    else:
        print("No .xlsx files found in the directory.")
        return {'error': 'Error in extraction!'}



# print(tblrec('data/tbl2.jpg'))