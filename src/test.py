import os
from openai import OpenAI
from dotenv import load_dotenv
# .envファイルから環境変数を読み込む
load_dotenv()
# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
if api_key is None:
    raise ValueError("OPENAI_API_KEY環境変数が設定されていません。")




# send a ChatCompletion request to count to 100
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': '詩を作って'}
    ],
    temperature=0,
    stream=True  # again, we set stream=True
)
# create variables to collect the stream of chunks
collected_chunks = []
collected_messages = []
# iterate through the stream of events
for chunk in response:
    collected_chunks.append(chunk)  # save the event response
    chunk_message = chunk.choices[0].delta.content  # extract the message
    collected_messages.append(chunk_message)  # save the message
    print(f"request: {chunk_message}")  # print the delay and text

# clean None in collected_messages
collected_messages = [m for m in collected_messages if m is not None]
full_reply_content = ''.join([m for m in collected_messages])
print(f"Full conversation received: {full_reply_content}")