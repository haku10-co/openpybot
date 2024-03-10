from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pypenai import process_user_input
from sqlcov import create_connection, save_conversation

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('input')
def handle_input(data):
    user_input = data.get('user_input')
    previous_conversation = data.get('previous_conversation', '')
    user_ip = request.remote_addr
    sid = request.sid  # 現在のクライアントのセッションIDを取得

    # コールバック関数を定義
    def send_response_chunk(chunk):
        emit('response', {'response': chunk}, room=sid)

    # コールバック関数を渡してprocess_user_inputを呼び出す
    process_user_input(user_input, previous_conversation, send_response_chunk, user_ip)

    # 処理が完了したことをクライアントに通知
    emit('response_complete', {'message': 'Processing complete'}, room=sid)

    # データベースに会話とクライアントのIPアドレスを保存
    conn = create_connection('conversations.db')
    save_conversation(conn, user_ip, user_input, "")  # システムの応答は別途保存
    conn.close()

    return jsonify({"status": "success"})

@app.route('/')
def index():
    return "Welcome to the chatbot server!"

if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost', port=3005)