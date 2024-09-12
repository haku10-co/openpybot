from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()
# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

def get_relevant_documents(query):
    # スクリプトのあるディレクトリを基点としてパスを設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    directory_path = os.path.join(current_dir, "nDoc")
    
    # .txt、.csv、.pdfファイルを探索
    files = [f for f in os.listdir(directory_path) if f.endswith(('.txt', '.csv', '.pdf'))]

    # ドキュメントローダーを初期化し、全てのファイルを読み込む
    documents = []
    for file in files:
        file_path = os.path.join(directory_path, file)
        if file.endswith('.txt'):
            loader = TextLoader(file_path)
            loaded_document = loader.load()
        elif file.endswith('.csv'):
            loader = CSVLoader(file_path)
            loaded_document = loader.load()
        elif file.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            loaded_document = loader.load_and_split()
        documents.extend(loaded_document)

    # テキストを適切なチャンクサイズに分割するためのTextSplitterを設定
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,  # PDFに対応するため、チャンクサイズを大きくしました
        chunk_overlap=200,
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
    docs = retriever.get_relevant_documents(query)
    return docs