import sqlite3

def create_connection(db_file):
    """データベースファイルへの接続を作成します。"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """会話を保存するためのテーブルを作成します。"""
    try:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            user_input TEXT,
            gpt_response TEXT
        )
        ''')
    except sqlite3.Error as e:
        print(e)

def save_conversation(conn, user_id, user_input, gpt_response):
    """ユーザーの識別情報、入力、およびGPTの応答をデータベースに保存します。"""
    try:
        c = conn.cursor()
        c.execute('INSERT INTO conversations (user_id, user_input, gpt_response) VALUES (?, ?, ?)', (user_id, user_input, gpt_response))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def get_latest_conversation(conn, user_id):
    """指定されたユーザーIDの最新の会話を取得します。"""
    try:
        c = conn.cursor()
        c.execute('SELECT user_input, gpt_response FROM conversations WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
        result = c.fetchone()
        if result:
            return result
        else:
            return None
    except sqlite3.Error as e:
        print(e)
        return None