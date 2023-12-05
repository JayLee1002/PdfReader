import requests
import json

def test_server_api(server_url, data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(server_url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 如果返回的状态码不是 200，会抛出异常
        print("Server Response:")
        print(response.text)
        return eval(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

if __name__ == "__main__":
    # 替换成你的服务器地址和端口号
    server_url = "http://10.70.23.213:8080/"

    # 定义要传递给服务器的 JSON 参数
    data = {'name': 'Attention is all you need'}

    # 调用测试函数
    lst = test_server_api(server_url, data)
