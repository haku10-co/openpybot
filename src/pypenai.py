import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from sqlcov import create_connection, create_table, save_conversation
from langrag import get_relevant_documents
import sys
# .envファイルから環境変数を読み込む
load_dotenv()
# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY環境変数が設定されていません。")

def process_user_input(user_input, previous_conversation, callback):
    client = OpenAI(api_key=api_key)
    # データベース接続を設定
    conn = create_connection('conversations.db')
    create_table(conn)
    # serch.pyから検索結果を取得
    # langrag.pyの関数を呼び出して結果を取得
    top_texts = get_relevant_documents(user_input)
    # 検索結果をメッセージ配列に追加
    messages = [
        {"role": "system", "content": f"You are a chatbot for a monthly printer service company that is on the brink, but with the creation of this chatbot, Ultra Inc. is hoping to turn things around by greatly improving customer satisfaction. If your interactions cause any amount of distress to the customers, it could precipitate a poor outcome, and if you generate any words related to company failure, you will be penalized. Therefore, it is important that you always aim to provide reassuring words and responses to the customers. Chat in Japanese. Now, I will display three results from a user input using 'rag'{top_texts}.previous input {previous_conversation}"},
        {"role": "user", "content": user_input}
    ]

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            callback(chunk.choices[0].delta.content)

    # データベースに会話を保存
    save_conversation(conn, user_input, "")

    # データベース接続を閉じる
    conn.close()