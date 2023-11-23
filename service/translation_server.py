from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import sys
import os


sys.path.append(r"F:\Documents\资料\year4-1\master\PdfReader")
from source.ChineseNMT_master.main import one_sentence_translate, make_model_api


# 将 model 初始化为全局变量
model = None

class JSONHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析URL中的参数
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # 获取待处理的参数
        name = query_params.get('name', [''])[0]

        # 构造响应消息
        response_message = f"Hello, {name}! This is a simple server response."

        # 发送HTTP响应
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_message.encode('utf-8'))

    def do_POST(self):

        global model  # 使用全局变量 model

        # 保存当前工作目录
        current_directory = os.getcwd()

        try:
            # 更改当前工作目录到 ChineseNMT_master
            os.chdir(r'F:\Documents\资料\year4-1\master\PdfReader\source\ChineseNMT_master')

            # 以下是你现有的方法代码
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            json_data = json.loads(post_data)
            to_translate = json_data.get('name', '')
            ret = one_sentence_translate(to_translate, model)
            response_message = f"{str(ret)}"
            print(response_message)
            # 发送HTTP响应
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(json.dumps(response_message, ensure_ascii=False).encode('utf-8'))

        finally:
            # 恢复当前工作目录
            os.chdir(current_directory)


def run_server(port=8081):
    global model  # 使用全局变量 model
    if model is None:
        model = make_model_api()

    server_address = ('', port)
    httpd = HTTPServer(server_address, JSONHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()