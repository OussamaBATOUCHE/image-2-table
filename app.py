from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from fncts import tblrec

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/tblrec', methods=['POST'])
def tblrec_api():
    if 'file' not in request.files or 'type' not in request.form:
        return jsonify({'error': 'Missing file or type parameter'}), 400

    file = request.files['file']
    file_type = request.form['type']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # return jsonify({'msg': 'It works!'})
        filename = secure_filename(file.filename)
        file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")

        extracted_file_path = tblrec(f"{app.config['UPLOAD_FOLDER']}/{filename}")
        result = 0
        if file_type == 'xlsx':
            return send_file(extracted_file_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # return result
        elif file_type == 'json':
            return jsonify({'warning': 'This format is Not available yet'}), 200
            df = pd.DataFrame(result)
            return df.to_json(orient='records')
        elif file_type == 'csv':
            return jsonify({'warning': 'This format is Not available yet'}), 200
            df = pd.DataFrame(result)
            return df.to_csv(index=False)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
