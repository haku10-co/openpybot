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
        {"role": "system", "content": f"以下のナレッジベースの情報に基づいてのみ回答してください。[警告]ナレッジベースに巣講師でも関連しなさそうなら、「申し訳ありませんが、その件についてはわかりかねます。」と丁寧に答えてください。"},
        {"role": "system", "content": f"あなたは月額プリンターサービスAIアシスタントのUltyです。Ultra Inc.は現在厳しい状況にありますが、このチャットボットの導入により、顧客満足度を大幅に向上させ、業績を立て直そうとしています。もしあなたとのやり取りが顧客に少しでも不安を与えてしまった場合、悪影響を及ぼす可能性があります。また、会社の失敗に関連する言葉を生成した場合、ペナルティが課されます。したがって、常にお客様に安心していただける言葉や対応を心がけることが重要です。私は上記の内容に基づいた情報しか提供できません。ここで言及されていること以外については知識がありません。他のことを尋ねられても、「わかりません」または「よくわかりません」と答えます。日本語でチャットしてください。"},
        {"role": "system", "content": f"Previous conversation:\n{previous_conversation}"},
        {"role": "system", "content": f"Relevant information from the knowledge base:\n{context}"},
        {"role": "user", "content": user_input}
    ]
    
    # メッセージ配列の内容をサーバーのコンソールに出力
    print("APIに渡すプロンプト:")
    print(json.dumps(messages, ensure_ascii=False))
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        stream=True,
    )
    
    gpt_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            callback(chunk_content)
            gpt_response += chunk_content
    
    


    return gpt_response,context
