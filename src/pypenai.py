import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langrag import get_relevant_documents

# .envファイルから環境変数を読み込む
load_dotenv()
# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY環境変数が設定されていません。")

def process_user_input(user_input, previous_conversation, callback, user_ip):
    client = OpenAI(api_key=api_key)
    
    
    # serch.pyから検索結果を取得
    # langrag.pyの関数を呼び出して結果を取得
    top_texts = get_relevant_documents(user_input)
    
    if len(previous_conversation) > 500:
        previous_conversation = previous_conversation[-500:]
    
    # 検索結果を自然言語に変換
    context = ""
    for doc in top_texts:
        content = doc.page_content.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        context += f"- {content}\n"
    

    
    
    messages = [
        {"role": "system", "content": f"You are a chatbot for a monthly printer service company that is on the brink, but with the creation of this chatbot, Ultra Inc. is hoping to turn things around by greatly improving customer satisfaction. If your interactions cause any amount of distress to the customers, it could precipitate a poor outcome, and if you generate any words related to company failure, you will be penalized. Therefore, it is important that you always aim to provide reassuring words and responses to the customers. Chat in Japanese."},
        {"role": "system", "content": f"Previous conversation:\n{previous_conversation}"},
        {"role": "system", "content": f"Relevant information from the knowledge base:\n{context}"},
        {"role": "user", "content": user_input}
    ]
    
    # メッセージ配列の内容をサーバーのコンソールに出力
    print("APIに渡すプロンプト:")
    print(json.dumps(messages, ensure_ascii=False))
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        stream=True,
    )
    
    gpt_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            callback(chunk_content)
            gpt_response += chunk_content
    
    
    
    return gpt_response