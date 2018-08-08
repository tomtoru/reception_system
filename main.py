# -*- coding: utf-8 -*-

import subprocess
import socket
import xml.etree.ElementTree as ET
import time

import requests
import json

from config.setting import WEBHOOK_URL


# とりあえずlocalhost
host = '127.0.0.1'
port = 10500

# 社員名を設定
members = [
    u"鈴木",
    u"佐藤",
    u"冨永"
]

def main():
    # julius起動スクリプト
    process = subprocess.Popen(["sh ./start_julius.sh"], stdout=subprocess.PIPE, shell=True)
    process_id = process.stdout.read().decode('utf-8')
    time.sleep(3)


    # TCPクライアントの作成と接続
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # XML解析
    try:
        data = ''
        print("please speak")
        while 1:
            # ...</RECOGOUT> までが格納されたdataを解析する
            if '</RECOGOUT>\n.' in data:
                root = ET.fromstring('<?xml version="1.0"?>\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
                print("!")

                for whypo in root.findall('./SHYPO/WHYPO'):
                    word = whypo.get('WORD')
                    score = float(whypo.get('CM'))

                    if word in members and score >= 0.9:
                        print("recognize:" + word)

                        #  webhook API を利用してslackに通知
                        requests.post(WEBHOOK_URL, data=json.dumps({
                            'text': word + u'さんに来客です!',
                            'username': u'受付システム',
                            'links_names': 1,
                        }))

                # 認識結果に社員名が含まれないときはdataを初期化
                data = ''
            else:
                data += str(client.recv(1024).decode('utf-8'))
                print(data)

    except KeyboardInterrupt:
        process.kill()
        subprocess.call(["kill " + process_id], shell=True)
        client.close()


if __name__ == "__main__":
    main()
