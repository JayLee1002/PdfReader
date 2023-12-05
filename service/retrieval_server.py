from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from translate import translate
import sys
import os
sys.path.append(r"F:\Documents\资料\year4-1\master\PdfReader")

from source.retrieval.similar_model import SimilarModel
# 将 sm 初始化为全局变量
sm = None

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
        global sm  # 使用全局变量 sm

        # 获取POST请求的数据长度
        content_length = int(self.headers['Content-Length'])

        # 读取POST请求的数据
        post_data = self.rfile.read(content_length).decode('utf-8')

        # 解析JSON数据
        json_data = json.loads(post_data)

        # 获取待处理的参数
        instruct = json_data.get('instruct', None)
        query = json_data.get('query', None)
        start_year = json_data.get('start_year', None)
        end_year = json_data.get('end_year', None)
        max_capacity = json_data.get('max_capacity', 50)
        target_capacity = json_data.get('target_capacity', 10)
        debug_mode = json_data.get('debug_mode', False)
        retry_times = json_data.get('retry_times', 3)

        # 检索
        ret = sm.crawler(instruct=instruct,
                         query=query,
                         start_year=start_year,
                         end_year=end_year,
                         max_capacity=max_capacity,
                         target_capacity=target_capacity,
                         debug_mode=debug_mode,
                         retry_times=retry_times)

        # 构造响应消息
        response_message = f"{ret}"

        # 发送HTTP响应
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_message.encode('utf-8'))

def run_server(port=8080):
    global sm  # 使用全局变量 sm
    if sm is None:
        sm = SimilarModel(r"F:\Documents\资料\year4-1\master\PdfReader\source\retrieval\sbert")
        sm.model = sm.model.cuda()

    server_address = ('', port)
    httpd = HTTPServer(server_address, JSONHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()