import os
# import cv2
# from paddleocr import PPStructure,draw_structure_result,save_structure_res
# from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
from datetime import datetime
import re

#----------------------------- For GPT version
from openai import OpenAI
import os 
import json
import base64
import requests

APIKEY=os.environ.get("OPENAI_API_KEY")

# Function to read prompt
def get_prompt(id):
    with open('../../../Vars_store/at_prompts.json', 'r') as file:
        prompt_version = json.load(file)
        return prompt_version[id]["text"]
    
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
#----------------------------- END For GPT version

# Function to convert Excel file to JSON
def excel_to_json(excel_file_path):
    import pandas as pd
    # Read Excel file
    df = pd.read_excel(excel_file_path)
    
    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records')
    return json_data

def tblrec(img_path, save_folder= './output', lang='en', mode='consume'):
    # English image
    table_engine = PPStructure(layout=False, show_log=True, lang=lang)

    img = cv2.imread(img_path)
    result = table_engine(img)
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H%M%S")
    save_structure_res(result, save_folder, os.path.basename(formatted_datetime))

    print('Saved at:', save_folder+formatted_datetime)
    
    # Directory where Excel files are stored
    directory = save_folder+'/'+formatted_datetime

    # List files in the directory
    files = os.listdir(directory)

    # If the mode is consume, we return the html file
    if mode == 'consume':
        # Open the file
        txt_files = [file for file in files if file.endswith('.txt')]
        if txt_files:
            # Get the first .xlsx file
            first_txt_file = os.path.join(directory, txt_files[0])
            with open(first_txt_file, 'r') as file:
                # Read the content
                json_content = file.read()
                # Parse JSON
                json_data = json.loads(json_content)
                # Get the HTML part
                html_data = json_data['res']['html']
                # Return it!
                return html_data 
        

    # Else we return the xlsx file
    else:
        # Find the first .xlsx file
        xlsx_files = [file for file in files if file.endswith('.xlsx')]

        if xlsx_files:
            # Get the first .xlsx file
            first_xlsx_file = os.path.join(directory, xlsx_files[0])
            
            # Convert Excel to JSON (we might need it in the future)
            # json_data = excel_to_json(first_xlsx_file)
            
            # Rename Excel file to 'extracted.xlsx'
            new_xlsx_file = os.path.join(directory, 'extracted.xlsx')
            os.rename(first_xlsx_file, new_xlsx_file)
        
            # Write JSON data to a file (we might need it in the future)
            # json_output_file = os.path.splitext(first_xlsx_file)[0] + '.json'
            # with open(json_output_file, 'w') as json_file:
            #     json_file.write(json_data)
            
            print(f"Excel file '{first_xlsx_file}' renamed to : '{new_xlsx_file}'")
            return new_xlsx_file 
        else:
            print("No .xlsx files found in the directory.")
            return {'error': 'Error in extraction!'}

# print(tblrec('data/tbl2.jpg'))

################### GPT version
def tblrec_gpt(img_path, save_folder= './output', lang='en', mode='consume', scan_id='undefined'):
    
    # Path to your image
    image_path = img_path

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Authorization": f"Bearer {APIKEY.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": get_prompt("v3")
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    # "max_tokens": 800
    }

    # Send the request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    res = response.json()
    content = res['choices'][0]['message']['content']
    content = re.sub(r'^```json\s*|\s*```$', '', content).strip()
    # print(content)

    # Saving folder
    directory = save_folder+'/d_'+scan_id

    data = {}
    # Parse the JSON content to ensure it is valid
    try:
        data = json.loads(content)
        base_name = os.path.basename(img_path)
        name, _ = os.path.splitext(base_name)
        data['scan_id'] = scan_id
        data['savedat'] = directory

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H%M%S")
        data['created'] = formatted_datetime

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Save the parsed JSON content to a file
        with open(directory+'/'+scan_id+'.json', 'w') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        print("JSON content saved to "+directory+'/'+scan_id+".json")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")

    return data 


def find_folder_ending_with(scan_id):
    for root, dirs, files in os.walk('./output'):
        for dir_name in dirs:
            if dir_name.endswith(scan_id):
                return os.path.join(root, dir_name)
    return None