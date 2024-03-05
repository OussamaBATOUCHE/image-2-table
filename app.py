from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from fncts import tblrec

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_LANGUAGES = {'en'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_lang(filelang):
    return filelang in ALLOWED_LANGUAGES

@app.route('/api/extract_table', methods=['POST'])
def tblrec_api():
    if 'file' not in request.files or 'type' not in request.form or 'lang' not in request.form:
        return jsonify({'error': 'Missing file, type or lang parameters'}), 400

    file = request.files['file']
    file_type = request.form['type']
    file_lang = request.form['lang']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if allowed_lang(file_lang) == False:
        return jsonify({'error': 'Language not supported. Try:'+str(ALLOWED_LANGUAGES)}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if file_type == 'xlsx':
            file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
            extracted_file_path = tblrec(f"{app.config['UPLOAD_FOLDER']}/{filename}", lang=file_lang)
            return send_file(extracted_file_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # return result
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
