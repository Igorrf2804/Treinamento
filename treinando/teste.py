import requests

url = 'http://127.0.0.1:8000/visualizarSetores/'

# data = {
#     'nome' : 'RH',
#     'pessoas' : [PessoaSerializer(Pessoa.objects.get(id = 1))]
# }
# response = requests.post(url, data=data)
response = requests.get(url)
print(response.json())