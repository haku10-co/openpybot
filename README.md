# プロジェクトのセットアップ方法

この文書では、Node.jsからPythonに書き換えたチャットボットプロジェクトのセットアップ方法について説明します。このプロジェクトは、OpenAIのAPIを利用しています。

## 必要な前提条件

- Python 3.8 以上がインストールされていること
- pip がインストールされていること
- OpenAIのAPIキーを取得していること

## 環境設定

1. このリポジトリをクローンまたはダウンロードします。

    ```bash
    git clone [リポジトリURL]
    cd [プロジェクトフォルダ]
    ```

2. 必要なPythonパッケージをインストールします。

    ```bash
    pip install -r requirements.txt
    ```

3. 環境変数を設定します。`.env` ファイルをプロジェクトのルートディレクトリに作成し、以下のようにOpenAIのAPIキーを設定してください。

    ```
    OPENAI_API_KEY=あなたのAPIキー
    ```

## サーバーの起動

1. サーバーを起動します。

    ```bash
    python server.py
    ```

2. ブラウザで `http://localhost:5005` にアクセスして、チャットボットを使用します。

## プロジェクトの概要

このチャットボットは、RAG(Retrieval-Augmented Generation)を利用し、ユーザーの質問に対して詳細な回答を生成します。`index.html` からユーザーの質問を入力すると、サーバー側で処理され、OpenAI APIを通じて回答が生成され、ユーザーに表示されます。



# openpybot
