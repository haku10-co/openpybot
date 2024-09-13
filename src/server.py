from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pypenai import process_user_input
from sqlcov import create_connection, save_conversation
import re
import os
import requests
import uuid

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_or_create_user_id():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    allowed_extensions = ['.txt', '.csv', '.pdf']
    if file and any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        filename = file.filename
        # 安全なファイル名を生成するための正規表現を使用
        filename = re.sub(r'[^\w\s.()-]', '', filename)
        save_dir = 'src/nDoc'
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)  # 元のファイル名を使用
        file.save(save_path)
        return jsonify({"status": "success", "message": "File saved successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid file format. Only .txt, .csv, and .pdf files are allowed."}), 400

@app.route('/list-files', methods=['GET'])
def list_files():
    save_dir = 'src/nDoc'
    try:
        # ディレクトリ内のファイル名をリスト化
        files = os.listdir(save_dir)
        # フルパスではなく、ファイル名のみを返す
        files = [file for file in files if os.path.isfile(os.path.join(save_dir, file)) and file.lower().endswith(('.txt', '.csv', '.pdf'))]
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/delete-file', methods=['POST'])
def delete_file():
    filename = request.json.get('filename')
    save_dir = 'src/nDoc'
    file_path = os.path.join(save_dir, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"status": "success", "message": "File deleted successfully"})
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404
    
@app.route('/get-file-content', methods=['POST'])
def get_file_content():
    filename = request.json.get('filename')
    save_dir = 'src/nDoc'
    file_path = os.path.join(save_dir, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return jsonify({"status": "success", "content": content})
        except Exception as e:
            return jsonify({"status": "error", "message": "Failed to read file: " + str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404
    
@socketio.on('input')
def handle_input(data):
    user_input = data.get('user_input')
    previous_conversation = data.get('previous_conversation', '')
    user_ip = request.remote_addr
    sid = request.sid

    # ユーザーIDを取得または生成
    user_id = get_or_create_user_id()

    def send_response_chunk(chunk):
        emit('response', {'response': chunk}, room=sid)

    gpt_response, context = process_user_input(user_input, previous_conversation, send_response_chunk, user_ip)

    emit('response_complete', {'message': 'Processing complete', 'context': context, 'user_id': user_id}, room=sid)

    send_conversation_to_gas(user_input, gpt_response, user_id)

def send_conversation_to_gas(question, answer, user_id):
    url = "https://script.google.com/macros/s/AKfycbzEPiKYx6xgaxz64LYUzny7Rgyh4nHGrNfiC6l4Z-Uege53xOwRJKBUYMl5sxZ1zbtFfA/exec"
    data = {
        "question": question,
        "answer": answer,
        "user_id": user_id
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("会話がGoogle Apps Scriptに正常に送信されました。")
    except requests.exceptions.RequestException as e:
        print(f"Google Apps Scriptへの送信中にエラーが発生しました: {e}")

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    user_id = get_or_create_user_id()
    response = jsonify({'user_id': user_id})
    response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Strict')  # 1年間有効
    return response

@app.route('/')
def index():
    return send_file('web/index.html')

@app.route('/contents/<path:filename>')
def serve_static(filename):
    return send_from_directory('../contents', filename)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=3005)