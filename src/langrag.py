from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv
# .envファイルから環境変数を読み込む
load_dotenv()
# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")
def get_relevant_documents(query):
    # /Users/kamehaku/Desktop/ultra/pypenai/src/documents/nDoc内のtxtファイルを探索
    directory_path = "./src/documents/nDoc"
    txt_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]

    # ドキュメントローダーを初期化し、全てのtxtファイルを読み込む
    documents = []
    for txt_file in txt_files:
        file_path = os.path.join(directory_path, txt_file)
        loader = TextLoader(file_path)
        loaded_document = loader.load()
        documents.extend(loaded_document)


    # テキストを適切なチャンクサイズに分割するためのTextSplitterを設定
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=200,  
        chunk_overlap=50,
        length_function=len,  
        is_separator_regex=False
    )

    split_documents = text_splitter.split_documents(documents)

    # OpenAIEmbeddingsオブジェクトを作成
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # FAISSベクトルストアを初期化し、ドキュメントをベクトル化して保存
    faiss_index = FAISS.from_documents(split_documents, embeddings)
    retriever = faiss_index.as_retriever(
        search_kwargs={'k': 5}
    )
    docs=retriever.get_relevant_documents(query)
    return docs