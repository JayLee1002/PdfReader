import threading
import time
from TR_Utils.controller import con
import sys
from pathlib import Path

fp = Path(__file__)
sys.path.append(str(fp.parent.parent.parent))

from service.translation_request import test_server_api as trans_server_api

# 替换成你的服务器地址和端口号
server_url = "http://10.70.23.213:8081/"

class WatchClip(threading.Thread):
    def __init__(self):
        super(WatchClip, self).__init__()
        self.name = ""
        self.expire = False
        self.text = ''

    def run(self):
        recent_text = self.text
        while True and not self.expire:
            cur_text = self.text
            if cur_text == recent_text:
                time.sleep(0.1)
            else:
                recent_text = cur_text
                self.update(cur_text)

    def setTranslateText(self, inputText):
        self.text = inputText

    def update(self, cur_text):
        data = {"name": cur_text}
        con.translationChanged.emit(trans_server_api(server_url, data))

    def expired(self):
        self.expire = True
