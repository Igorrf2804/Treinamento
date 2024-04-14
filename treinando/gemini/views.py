

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, UsuarioSerializer, PessoaSerializer, SetorSerializer, IndicadorSerializer, RelatorioSerializer, ScriptsSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Usuario, Pessoa, Setor, Indicador, Relatorio
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
# Create your views here.

GOOGLE_API_KEY = "AIzaSyCLOvpQv7soejToFewHRrAWRaUkUVYQu3g"

class PerguntaViewSet(viewsets.ModelViewSet):
    queryset = Pergunta.objects.all()
    serializer_class = PerguntaSerializer

    @csrf_exempt
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = request.data.get('user')
        pergunta_txt = request.data.get('pergunta')
        pergunta = serializer.instance

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        chat.send_message('Você é o Chatbot customizado da empresa CoordenaAgora, a partir de agora você irá responder perguntas com x informações, e caso sejam mandados prompt que não sejam relacionados a área da educação você irá responder: "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos", obs isso inclui perguntas que não tem haver com problemas como histórico escolar, encaminhamento, agendamento, comunicar ao coordenador etc')
        resposta = chat.send_message(pergunta_txt)

        if resposta.candidates[0].content.parts[0].text != "" and "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" not in resposta.candidates[0].content.parts[0].text:
            print(resposta.candidates[0].content.parts[0].text)
            pergunta.resposta = resposta.candidates[0].content.parts[0].text
            return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)
            #return Response({'mensagem': 'deu ruim'})

        return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ModelViewSet):
    #queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        usuario = request.data.get("usuario")
        senha = request.data.get("senha")
        if (Usuario.objects.filter(usuario = usuario, senha = senha).exists()):
            return Response({'resultado' : True}, status= status.HTTP_200_OK)
        else:
            return Response({'resultado' : False}, status= status.HTTP_404_NOT_FOUND)


    

@api_view(['GET'])
def listar_scripts(request):

        # http://127.0.0.1:8000/api/scripts

    if request.method == 'GET':

        scripts = Script.objects.all()                          # Get all objects in User's database (It returns a queryset)

        serializer = ScriptsSerializer(scripts, many=True)       # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)                    # Return the serialized data
        
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_script(request):

        # http://127.0.0.1:8000/api/cadastrar-script

        # {
        #     "nome": "oi",
        #     "descricao": "oi"
        # }

    if request.method == 'POST':
        serializer = ScriptsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['PUT'])
def editar_script(request, id):

        # http://127.0.0.1:8000/api/editar-script/1

    print("id", id)
    print("request", request.data)

    try:
        id = Script.objects.get(id=id)
    except Script.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ScriptsSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_pessoas(request):

        # http://127.0.0.1:8000/api/scripts

    if request.method == 'GET':

        scripts = Pessoa.objects.all()                          # Get all objects in User's database (It returns a queryset)

        serializer = PessoaSerializer(scripts, many=True)       # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)                    # Return the serialized data
        
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_pessoa(request):

        # http://127.0.0.1:8000/api/cadastrar-script

        # {
        #     "nome": "oi",
        #     "descricao": "oi"
        # }

    if request.method == 'POST':
        serializer = PessoaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def listar_indicadores(request):

        # http://127.0.0.1:8000/api/scripts

    if request.method == 'GET':

        scripts = Indicador.objects.all()                          # Get all objects in User's database (It returns a queryset)

        serializer = IndicadorSerializer(scripts, many=True)       # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)                    # Return the serialized data
        
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_indicador(request):

        # http://127.0.0.1:8000/api/cadastrar-script

        # {
        #     "nome": "oi",
        #     "descricao": "oi"
        # }

    if request.method == 'POST':
        serializer = IndicadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)













class PessoaViewSet(viewsets.ModelViewSet):
    #queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer

class SetorViewSet(viewsets.ModelViewSet):
    #queryset = Setor.objects.all()
    serializer_class = SetorSerializer

class IndicadorViewSet(viewsets.ModelViewSet):
    #queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer

class RelatorioViewSet(viewsets.ModelViewSet):
    #queryset = Relatorio.objects.all()
    serializer_class = RelatorioSerializer