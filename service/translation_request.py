import requests
import json

def test_server_api(server_url, data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(server_url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 如果状态码不是 200，会引发异常

        # 显式设置编码
        response.encoding = 'utf-8'

        print("服务器响应:")
        print(response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"连接服务器时发生错误: {e}")

if __name__ == "__main__":
    # 替换成你的服务器地址和端口号
    server_url = "http://10.70.23.213:8081/"

    # 定义要传递给服务器的 JSON 参数
    data = {'name': 'I love you.'}

    # 调用测试函数
    text = test_server_api(server_url, data)
