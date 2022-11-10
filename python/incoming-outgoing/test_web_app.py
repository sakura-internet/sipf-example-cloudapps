import unittest
import json
import os
import sqlite3
import contextlib
import constants
from db import create_table, save_message, fetch_messages
from constants import TABLE_NAME
from web_app import app
from unittest.mock import patch

TEST_DB_FILENAME = "test.db"

UNIT_MESSAGE = {
        "device_id": "1234567890",
        "timestamp_src": "2022-03-24T00:00:00.000Z",
        "type": "object",
        "id": "abcdef12-3456-abcd-1234-abcde1234567",
        "payload": [
            {
                "type": "string.utf8",
                "tag": "FF",
                "value": "this is test case"
            }
        ]
}


class DBTest(unittest.TestCase):

    def setUp(self) -> None:
        create_table(file_name=TEST_DB_FILENAME)

    def tearDown(self) -> None:
        os.remove(TEST_DB_FILENAME)

    def test_create_database(self) -> None:
        create_table(file_name=TEST_DB_FILENAME)

        # DB ファイルを作成して、ファイルが存在する
        db_exists = os.path.exists(TEST_DB_FILENAME)
        self.assertEqual(db_exists, True)

    def test_save_message(self) -> None:
        save_message(TEST_DB_FILENAME, UNIT_MESSAGE)

        select_query = f"SELECT * FROM {TABLE_NAME}"

        with contextlib.closing(
                sqlite3.connect(TEST_DB_FILENAME)) as conn, conn:
            conn.row_factory = sqlite3.Row
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(select_query)
                result = cur.fetchall()

        # messages に レコードを保存して、SQLite 上に message が存在する
        self.assertEqual(len(result) == 1, True)

    def test_fetch_messages(self) -> None:
        fetch_number = 10
        for i in range(fetch_number):
            save_message(TEST_DB_FILENAME, UNIT_MESSAGE)

        result = fetch_messages(file_name=TEST_DB_FILENAME,
                                number=fetch_number)
        # 10 件メッセージが取得できている
        self.assertEqual(len(result) == fetch_number, True)


class APITest(unittest.TestCase):

    def setUp(self) -> None:
        create_table(file_name=TEST_DB_FILENAME)
        # テストのために適当な id と token を作る
        self.device_id = "11111111"
        self.incoming_token = "aaaaa-aaaaa-aaaaa-aaaa"
        # テスト用の環境変数をセット
        os.environ["DEVICE_ID"] = self.device_id
        os.environ["INCOMING_TOKEN"] = self.incoming_token

    def tearDown(self) -> None:
        os.remove(TEST_DB_FILENAME)

    # requests.post を 200 を返すように
    @patch("requests.post")
    # DB_FILE_NAME を 'test.db' を上書き
    @patch("constants.DB_FILE_NAME", TEST_DB_FILENAME)
    def test_post(self, mock_post) -> None:
        mock_post.return_value.status_code = 200
        test_client = app.test_client(self)

        # platform に送信用のメッセージ
        message = UNIT_MESSAGE.copy()
        message["device_id"] = self.device_id
        message["payload"][0] = {
            "type": "string.utf8",
            "tag": "00",
            "value": "this is message for platform"
        }

        response = test_client.post('/', content_type='application/json', data=json.dumps(message))
        # post した結果が 200
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
