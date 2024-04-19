from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, UsuarioSerializer, PessoaSerializer, SetorSerializer, IndicadorSerializer, \
    RelatorioSerializer, ScriptsSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Usuario, Pessoa, Setor, Indicador, Relatorio
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
import random

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
        chat.send_message(
            'Você é o Chatbot customizado da empresa CoordenaAgora, a partir de agora você irá responder perguntas com x informações, e caso sejam mandados prompt que não sejam relacionados a área da educação você irá responder: "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos", obs isso inclui perguntas que não tem haver com problemas como histórico escolar, encaminhamento, agendamento, comunicar ao coordenador etc')
        resposta = chat.send_message(pergunta_txt)

        if resposta.candidates[0].content.parts[
            0].text != "" and "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" not in \
                resposta.candidates[0].content.parts[0].text:
            print(resposta.candidates[0].content.parts[0].text)
            pergunta.resposta = resposta.candidates[0].content.parts[0].text
            return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)
            # return Response({'mensagem': 'deu ruim'})

        return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ViewSet):
    # queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        usuario = request.data.get("usuario")
        senha = request.data.get("senha")
        if (Usuario.objects.filter(usuario=usuario, senha=senha).exists()):
            return Response({'resultado': True}, status=status.HTTP_200_OK)
        else:
            return Response({'resultado': False}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def recuperar_senha(self, request):
        lista = []
        for i in range(0, 8):
            lista.append(random.randint(0, 9))
        print(lista)
        return Response({'resposta': 'Foi'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def listar_scripts(request):
    # http://127.0.0.1:8000/api/scripts

    if request.method == 'GET':
        scripts = Script.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = ScriptsSerializer(scripts,
                                       many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

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


@api_view(['DELETE'])
def excluir_script(request, id):
    try:
        id = Script.objects.get(id=id)
    except Script.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def listar_pessoas(request):
    # http://127.0.0.1:8000/api/scripts

    if request.method == 'GET':
        scripts = Pessoa.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = PessoaSerializer(scripts,
                                      many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

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
        scripts = Indicador.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = IndicadorSerializer(scripts,
                                         many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

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


@api_view(['GET'])
def visualizar_setores(request):

    if request.method == 'GET':
        scripts = Setor.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = SetorSerializer(scripts, many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def cadastrar_setores(request):
    # http://127.0.0.1:8000/api/cadastrar-script

    # {
    #     "nome": "oi",
    #     "descricao": "oi"
    # }

    if request.method == 'POST':
        serializer = SetorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_setores(request, id):
    # http://127.0.0.1:8000/api/editar-script/1

    print("id", id)
    print("request", request.data)

    try:
        id = Setor.objects.get(id=id)
    except Setor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = SetorSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
def excluir_setores(request, id):
    try:
        id = Setor.objects.get(id=id)
    except Setor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)





















class PessoaViewSet(viewsets.ModelViewSet):
    # queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer


class SetorViewSet(viewsets.ViewSet):
    # queryset = Setor.objects.all()
    serializer_class = SetorSerializer

    @api_view(['GET'])
    def visualizarSetores(self, request):
        serializer = SetorSerializer(Setor.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def cadastrarSetores(self, request):

        serializer = SetorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def editarSetores(self, request):

        try:
            setor = Setor.objects.get(id=request.data['id'])
        except Setor.DoesNotExist:
            return Response()

        serializer = SetorSerializer(setor, request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def excluirSetores(self, request):

        try:
            setor = Setor.objects.get(id=request.data['id'])
            setor.delete()
            return Response({'resultado': 'usuario deletado com sucesso!'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'resultado': 'falha ao deletar usuario!'}, status=status.HTTP_400_BAD_REQUEST)


class IndicadorViewSet(viewsets.ModelViewSet):
    # queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer


class RelatorioViewSet(viewsets.ModelViewSet):
    # queryset = Relatorio.objects.all()
    serializer_class = RelatorioSerializer

    @action(detail=False, methods=['post'])
    def enviarRelatorio(self, request):
        data = request.data
        serializer = RelatorioSerializer(data)


class TelaInicialViewSet(viewsets.ViewSet):
    queryset = {
        'informacoes': [],
        'setores': [],
        'pessoas': []
    }

    @action(detail=False, methods=['get'])
    def listarDados(self, request):
        setores = Setor.objects.all()
        pessoas = Pessoa.objects.all()
        serializerSetores = SetorSerializer(setores, many=True)
        serializerPessoas = PessoaSerializer(pessoas, many=True)

        for index in serializerSetores.data:
            self.queryset['setores'].append(index)
        for index in serializerPessoas.data:
            self.queryset['pessoas'].append(index)

        return Response({'data': self.queryset}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def editar_pessoa(request, id):
    print(id)

    try:
        id = Pessoa.objects.get(id=id)
    except Pessoa.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PessoaSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_pessoa(request, id):
    try:
        id = Pessoa.objects.get(id=id)
    except Pessoa.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def editar_indicador(request, id):
    print(id)

    try:
        id = Indicador.objects.get(id=id)
    except Indicador.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = IndicadorSerializer(id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def excluir_indicador(request, id):
    try:
        id = Indicador.objects.get(id=id)
    except Indicador.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        id.delete();
        return Response(status=status.HTTP_204_NO_CONTENT)







