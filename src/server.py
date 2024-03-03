from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pypenai import process_user_input
from sqlcov import create_connection, save_conversation, get_latest_conversation

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('input')
def handle_input(data):
    user_input = data.get('user_input')
    user_ip = request.remote_addr  # クライアントのIPアドレスを取得

    conn = create_connection('conversations.db')
    # 最新の会話を取得
    latest_conversation = get_latest_conversation(conn, user_ip)
    if latest_conversation:
        previous_conversation = latest_conversation[0]  # user_inputを前回の会話として使用
    else:
        previous_conversation = ""
     # コールバック関数を定義
    def send_response_chunk(chunk):
        emit('response', {'response': chunk}, broadcast=True)
    # コールバック関数を渡してprocess_user_inputを呼び出す
    process_user_input(user_input, previous_conversation, send_response_chunk)

    # 処理が完了したことをクライアントに通知
    emit('response_complete', {'message': 'Processing complete'}, broadcast=True)

    # データベースに会話とクライアントのIPアドレスを保存
    save_conversation(conn, user_ip, user_input, "")
    conn.close()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost', port=3005)