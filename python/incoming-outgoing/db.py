import contextlib
import sqlite3

from constants import TABLE_NAME, DB_FILE_NAME


def save_message(file_name: str = DB_FILE_NAME, message: dict = {}) -> None:
    """
    DB に モノプラから送信されたメッセージを保存します
    :param file_name: DBファイル名
    :param message: JSON 形式のモノプラからのメッセージ
    :return: None
    """
    query = f"INSERT INTO {TABLE_NAME} VALUES(?, ?, ?, ?, ?, ?)"
    values = [
        None,
        message["device_id"],
        message["timestamp_src"],
        message["type"],
        message["id"],
        str(message["payload"])
    ]
    with contextlib.closing(sqlite3.connect(file_name)) as conn, conn:
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute(query, values)


def fetch_messages(file_name: str = DB_FILE_NAME, number: int = 10) -> list:
    """
    messages テーブルから number 件レコードを取得します

    :param file_name: DB ファイル名
    :param number: 取得する件数
    :return:
    """
    query = f'SELECT * FROM {TABLE_NAME} ORDER BY ID DESC LIMIT {number}'
    with contextlib.closing(sqlite3.connect(file_name)) as conn, conn:
        conn.row_factory = sqlite3.Row
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute(query)
            return cur.fetchall()


def create_table(file_name: str = DB_FILE_NAME) -> None:
    """
    アプリケーションで利用する以下のようなテーブルを作成します。

    messages

    id INTEGER
    device_id VARCHAR
    timestamp_src VARCHAR
    msg_type VARCHAR
    """
    query = f"""
            CREATE TABLE IF NOT EXISTS
            {TABLE_NAME}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id VARCHAR,
                timestamp_src VARCHAR,
                msg_type VARCHAR,
                obj_id VARCHAR,
                payload TEXT
            )
            """
    with contextlib.closing(sqlite3.connect(file_name)) as conn, conn:
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute(query)
