from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json
from datetime import datetime
from fncts import tblrec, tblrec_gpt, find_folder_ending_with

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_LANGUAGES = {'en'}
ALLOWED_MODES = {'consume','api'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def verify_token(token):
    with open('../../../Vars_store/at_tkns.json', 'r') as file:
        list_of = json.load(file)
        return token in list_of['tkns']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_lang(filelang):
    return filelang in ALLOWED_LANGUAGES

def allowed_mode(filemode):
    return filemode in ALLOWED_MODES

@app.route('/api/extract_table', methods=['POST'])
def tblrec_api():
    if 'file' not in request.files or 'type' not in request.form or 'lang' not in request.form:
        return jsonify({'error': 'Missing file, type or lang parameters'}), 400

    file = request.files['file']
    file_type = request.form['type']
    file_lang = request.form['lang']
    file_mode = request.form['mode']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if allowed_mode(file_mode) == False:
        return jsonify({'error': 'Mode not supported.'}), 400
    
    if allowed_lang(file_lang) == False:
        return jsonify({'error': 'Language not supported. Try:'+str(ALLOWED_LANGUAGES)}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        if file_type == 'xlsx':
            file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
            extracted_file_path = tblrec_gpt(f"{app.config['UPLOAD_FOLDER']}/{filename}", lang=file_lang, mode=file_mode)
            return send_file(extracted_file_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # return result
        
        elif file_type == 'html':
            file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
            res = tblrec_gpt(f"{app.config['UPLOAD_FOLDER']}/{filename}", lang=file_lang, mode=file_mode)
            html_file = res['table']
            return jsonify(html_file), 200
        
        # Not Supported yet !!!
        elif file_type == 'json':
            return jsonify({'warning': 'This format is Not available yet'}), 200
            # df = pd.DataFrame(result)
            # return df.to_json(orient='records')
        elif file_type == 'csv':
            return jsonify({'warning': 'This format is Not available yet'}), 200
            # df = pd.DataFrame(result)
            # return df.to_csv(index=False)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/s2dv', methods=['POST'])
def s2dv_process():
    if 'scan_file' not in request.files or 'scan_id' not in request.form or 'tkn' not in request.form:
        return jsonify({'error': 'Missing parameter!'}), 400

    file = request.files['scan_file']
    scan_id = request.form['scan_id']
    token = request.form['tkn']

    if not verify_token(token):
        abort(403, description="Forbidden: Invalid token")

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if scan_id == '':
        return jsonify({'error': 'Scan Id is required'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
        res = tblrec_gpt(f"{app.config['UPLOAD_FOLDER']}/{filename}", scan_id=scan_id)
        return jsonify(res), 200

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/retrieve', methods=['POST'])
def s2dv_retrieve():
    if 'scan_id' not in request.form  or 'tkn' not in request.form:
        return jsonify({'error': 'Missing parameter!'}), 400
    scan_id = request.form['scan_id']
    token = request.form['tkn']

    if not verify_token(token):
        abort(403, description="Forbidden: Invalid token")
    

    file_folder_path = find_folder_ending_with(scan_id)
    if not file_folder_path:
        abort(404, description="Folder not found")
    # file_folder_path = os.path.join('./output/d_'+scan_id)

    # Check if the directory exists
    if not os.path.exists(file_folder_path):
        abort(404, description="Directory not found")

    # Get the first .json file in the directory
    json_files = [f for f in os.listdir(file_folder_path) if f.endswith(scan_id+'.json')]
    if not json_files:
        abort(404, description="No JSON files found in the directory")

    first_json_file = json_files[0]
    file_path = os.path.join(file_folder_path, first_json_file)

    # Read the file content and return it as JSON
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        abort(500, description=f"Error reading file: {str(e)}")

@app.route('/api/rename_sif', methods=['POST'])
def s2dv_rename_sif():
    if 'scan_id' not in request.form or 'scan_id_new' not in request.form  or 'tkn' not in request.form:
        return jsonify({'error': 'Missing parameter!'}), 400
    
    scan_id = request.form['scan_id']
    scan_id_new = request.form['scan_id_new']
    token = request.form['tkn']

    if not verify_token(token):
        abort(403, description="Forbidden: Invalid token")
    
    file_folder_path = find_folder_ending_with(scan_id)
    if not file_folder_path:
        abort(404, description="Folder not found")
    else:
        if file_folder_path.count('_') == 2:
            abort(404, description="Folder already renamed!")
        else:
            
            # Get the first .json file in the directory
            json_files = [f for f in os.listdir(file_folder_path) if f.endswith('.json')]
            if not json_files:
                abort(404, description="No JSON files found in the directory")

            first_json_file = json_files[0]
            file_path = os.path.join(file_folder_path, first_json_file)

            # Read the file content and update it
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H%M%S")
            with open(file_path, 'r') as file:
                data = json.load(file)
                data['update'] =formatted_datetime
                data['scan_id_old'] = data['scan_id']
                data['scan_id'] = scan_id_new
                data['savedat'] = file_folder_path+"_"+scan_id_new
                with open(file_folder_path+'/'+scan_id_new+'.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)

            # rename it
            os.rename(file_folder_path, file_folder_path+"_"+scan_id_new)
            # update the json file
            return jsonify(message="The folder was successfully renamed!")


@app.route('/')
def check():
    return 'Welcome to Scan.2.Digital.version program!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
