import os
import json
from urllib.parse import urljoin

import requests
from flask import Flask, Response, request, render_template

import constants
from db import fetch_messages, save_message, create_table

app = Flask(__name__)


def send_message_to_service_adaptor(device_id: str,
                                    incoming_url: str) -> Response:
    """
    モノプラ　Incoming Webhook に対して HTTP POST を送信します

    :param device_id: モノプラ device_id
    :param incoming_url: サービスアダプタのURL
    :return: HTTP request の response
    """
    message = {
        "device_id": device_id,
        "type": "object",
        "payload": [
            {
                "type": "string.utf8",
                "tag": "FF",
                "value": "message_from_server"
            }
        ]
    }
    resp = requests.post(incoming_url, data=json.dumps(message))
    # incoming webhook にへ response に失敗した場合は例外が発生する
    resp.raise_for_status()
    return resp


@app.route("/", methods=["GET"])
def index() -> str:
    """
    DB に保存されているメッセージを最新10件を取得して HTML を返します

    :return: template を返却します
    """

    # SQLite から 取得する
    result = fetch_messages(number=constants.NUMBER_OF_MESSAGES)
    return render_template('index.html', messages=result)


@app.route("/", methods=["POST"])
def post() -> Response:
    """
    DB にモノプラ Outgoing Webhook から送信されたメッセージを保存します

    :return: HTTP Response を返します
    """
    # SQLite にモノプラから送信されてきたメッセージを保存する
    save_message(file_name=constants.DB_FILE_NAME,message=request.json)

    # 環境変数から DEVICE_ID と TOKEN を取得する
    device_id = os.environ.get("DEVICE_ID")
    incoming_token = os.environ.get("INCOMING_TOKEN")

    incoming_url = urljoin(constants.BASE_INCOMING_URL, incoming_token)
    # service adaptor へ メッセージを送信
    send_message_to_service_adaptor(device_id=device_id,
                                    incoming_url=incoming_url)

    print("Message successfully sent")
    return Response(status=200, mimetype='application/json')


if __name__ == "__main__":
    create_table(constants.DB_FILE_NAME)
    app.run()
