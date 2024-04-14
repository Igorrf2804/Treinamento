import requests

url = 'http://127.0.0.1:8000/recuperarSenha/'
data = {'ola' : 'ola'}
response = requests.post(url, data=data)
print(response.json())