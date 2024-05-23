import requests

# Flask服务器的URL
url = 'http://localhost:5050/submit'

# 要发送的数据
data = 'This is a test string'

# 发送POST请求
response = requests.post(url, json={'data': data})

# 打印服务器响应
print(response.json())
