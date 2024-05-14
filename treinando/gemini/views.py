from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, CoordenadorSerializer, PessoaSerializer, SetorSerializer, \
    IndicadorSerializer, InstituicaoSerializer, CursoSerializer, AlunoSerializer, MensagemSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Coordenador, Pessoa, Setor, Indicador, Instituicao, Curso, Aluno, Mensagem
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
import random

# Create your views here.

GOOGLE_API_KEY = "AIzaSyCLOvpQv7soejToFewHRrAWRaUkUVYQu3g"
profissionais = [
    {
        "nome": "Roberto Medeira",
        "profissao": "Coordenador do curso de informática",
        "curso": "Informática",
        "profissão": "Desenvolvedor"
    }
]


#---------------------------------------------INTEGRAÇÃO COM A GEMINI--------------------------------------------#


@api_view(['POST'])
@csrf_exempt
def create(request):
    serializer = PerguntaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    user = request.data.get('user')
    pergunta_txt = request.data.get('pergunta')
    pergunta = serializer.instance

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    # Você é o Chatbot customizado da empresa CoordenaAgora, a partir de agora você irá responder perguntas
    # com x informações, e caso sejam mandados prompt que não sejam relacionados a área da educação você
    # irá responder: "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos", obs isso inclui
    # perguntas que não tem haver com problemas como histórico escolar, encaminhamento, agendamento, comunicar ao
    # coordenador etc

    scripts = Script.objects.all()
    serialized_data = []
    if len(scripts) > 0:
        for script in scripts:
            serializer = ScriptsSerializer(script)
            serialized_data.append(serializer.data)
    else:
        return Response({'mensagem': 'Não existem scripts cadastrados'}, status=status.HTTP_400_BAD_REQUEST)

    descricoes = [item['descricao'] for item in serialized_data]
    descricoes.append("Caso você não consiga realizar o atendimento por conta própria, realize um agendamento")

    chat.send_message(descricoes)
    resposta = chat.send_message(pergunta_txt)

    if resposta.candidates[0].content.parts[
        0].text != "" and "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" not in \
            resposta.candidates[0].content.parts[0].text:
        pergunta.resposta = resposta.candidates[0].content.parts[0].text
        #
        # if "encami" in pergunta.resposta.lower():
        #     for index in profissionais:
        #         print(index["nome"])
        #         if index['nome'] in pergunta.resposta:
        #             email = request.data.get('email')
        #             if Usuario.objects.filter(email=email).exists():
        #                 tema = 'Encaminhamento realizado para você para os dias x/y/2024'
        #                 msg = f'Um encaminhamento foi realizado para você para o atendimento do usuário {request.data.get("user")} nos dias x/y/2024, por favor entre em contato quando possível'
        #                 remetente = "ads.senac.tcs@gmail.com"
        #                 send_mail(assunto, mensagem, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
        #                 return Response({'mensagem': "O encaminhamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)
        #
        #     return Response({'mensagem': 'Ocorreu um erro ao realizar o encaminhamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)
        #
        # if "agend" in pergunta.resposta.lower():
        #     for index in profissionais:
        #         if index['nome'] in pergunta.resposta:
        #             email = request.data.get('email')
        #             if Usuario.objects.filter(email=email).exists():
        #                 tema = 'Reunião agendada para você para os dias x/y/2024'
        #                 msg = f'Um agendamento foi realizado para você para o atendimento do usuário {request.data.get("user")} no dia x/y/2024 as 18:00'
        #                 remetente = "ads.senac.tcs@gmail.com"
        #                 send_mail(assunto, mensagem, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
        #                 return Response({'mensagem': "O agendamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)

        # return Response({'mensagem': 'Ocorreu um erro ao realizar o agendamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)

        return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)

    return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)


#---------------------------------------------REDEFINIR SENHA--------------------------------------------#

@api_view(['POST'])
def redefinir_senha(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if (Coordenador.objects.filter(email=email).exists() or Aluno.objects.filter(email=email).exists()):
            codigo = gerar_codigo_verificacao()
            enviar_codigo_por_email(email, codigo)
            return Response(codigo, status=status.HTTP_201_CREATED)
        return Response("Usuário não encontrado", status=status.HTTP_400_BAD_REQUEST)
    return Response("Não foi possível enviar o código de verificação", status=status.HTTP_400_BAD_REQUEST)


def gerar_codigo_verificacao():
    return str(random.randint(10000000, 99999999))


def enviar_codigo_por_email(email, codigo):
    assunto = 'Código de verificação para redefinição de senha'
    mensagem = f'Seu código de verificação é: {codigo}'
    remetente = "ads.senac.tcs@gmail.com"
    send_mail(assunto, mensagem, remetente, recipient_list=[email, 'ads.senac.tcs@gmail.com'])


@api_view(['PUT'])
def alterar_senha(request):
    if request.method == 'PUT':
        email = request.data.get('email')
        senha = request.data.get('senha')

        usuarioCoordenador = Coordenador.objects.filter(email=email).exists()
        usuarioAluno = Aluno.objects.filter(email=email).exists()

        if(not usuarioAluno and not usuarioCoordenador):
            return Response("Usuário não encontrado", status=status.HTTP_404_NOT_FOUND)

        if usuarioCoordenador:
            usuario = Coordenador.objects.get(email=email)
            dados = {'email': email, 'senha': senha, 'nome': usuario.nome, 'curso': usuario.curso_id, 'instituicao': usuario.instituicao_id}
            serializer = CoordenadorSerializer(usuario, data=dados)
        else:
            usuario = Aluno.objects.get(email=email)
            dados = {'email': email, 'senha': senha, 'nome': usuario.nome, 'curso': usuario.curso_id, 'instituicao': usuario.instituicao_id}
            serializer = AlunoSerializer(usuario, data=dados)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Método de solicitação inválido", status=status.HTTP_405_METHOD_NOT_ALLOWED)


#-------------------------------------------------CADASTRAR ALUNO------------------------------------------------#

@api_view(['POST'])
def cadastrar_aluno(request):
    if request.method == 'POST':
        email = request.data.get('email', None)
        if email:
            if Aluno.objects.filter(email=email).exists():
                return Response({"email": "Este e-mail já está em uso."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AlunoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#-------------------------------------------------INSTITUIÇÃO------------------------------------------------#

@api_view(['GET'])
def listar_instituicoes_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('instituicao', '')
        instituicoes = Instituicao.objects.filter(nome__icontains=nome_filtro)
        serializer = InstituicaoSerializer(instituicoes, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


#-------------------------------------------------CURSO------------------------------------------------#

@api_view(['GET'])
def listar_cursos_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('curso', '')
        cursos = Curso.objects.filter(nome__icontains=nome_filtro)
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


#-------------------------------------------------LOGIN------------------------------------------------#

class UsuarioViewSet(viewsets.ViewSet):
    serializer_class = CoordenadorSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        senha = request.data.get("senha")
        coordenadorEncontrado = Coordenador.objects.filter(email=email, senha=senha).first()
        alunoEncontrado = Aluno.objects.filter(email=email, senha=senha).first()
        if coordenadorEncontrado:
            serializer = CoordenadorSerializer(coordenadorEncontrado)
            return Response({'resultado': True, 'dadosDoUsuario': serializer.data}, status=status.HTTP_200_OK)
        elif alunoEncontrado:
            serializer = AlunoSerializer(alunoEncontrado)
            return Response({'resultado': True, 'dadosDoUsuario': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'resultado': False}, status=status.HTTP_404_NOT_FOUND)


#-------------------------------------------------SCRIPTS------------------------------------------------#


@api_view(['GET'])
def listar_scripts(request):
    if request.method == 'GET':
        scripts = Script.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = ScriptsSerializer(scripts,
                                       many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_script(request):
    if request.method == 'POST':
        serializer = ScriptsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_script(request, id):
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


#-----------------------------------------------PESSOAS------------------------------------------------#


@api_view(['GET'])
def listar_pessoas(request):
    if request.method == 'GET':
        pessoas = Pessoa.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = PessoaSerializer(pessoas,
                                      many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_pessoa(request):
    if request.method == 'POST':
        serializer = PessoaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_pessoas_por_ids(request):
    if request.method == 'GET':
        ids_list = request.GET.getlist('ids[]', [])  # Get the list of IDs from the query parameters
        pessoas = Pessoa.objects.filter(id__in=ids_list)
        serializer = PessoaSerializer(pessoas, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_pessoas_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('nome', '')  # Obtém o parâmetro 'nome' da query string
        pessoas = Pessoa.objects.filter(nome__icontains=nome_filtro)  # Filtra as pessoas com base no nome fornecido
        serializer = PessoaSerializer(pessoas, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_pessoa(request, id):
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


#--------------------------------------------INDICADORES------------------------------------------------#


@api_view(['GET'])
def listar_indicadores(request):
    if request.method == 'GET':
        indicadores = Indicador.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = IndicadorSerializer(indicadores,
                                         many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_indicador(request):
    if request.method == 'POST':
        serializer = IndicadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_indicadores_por_nome(request):
    if request.method == 'GET':
        nome_filtro = request.GET.get('nome', '')
        indicadores = Indicador.objects.filter(nome__icontains=nome_filtro)
        serializer = IndicadorSerializer(indicadores, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_indicador(request, id):
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


#------------------------------------------------SETORES------------------------------------------------#


@api_view(['GET'])
def visualizar_setores(request):
    if request.method == 'GET':
        scripts = Setor.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = SetorSerializer(scripts,
                                     many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

        return Response(serializer.data)  # Return the serialized data

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def cadastrar_setores(request):
    if request.method == 'POST':
        serializer = SetorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editar_setores(request, id):
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


#------------------------------------------------Salvar mensagem------------------------------------------------#
@api_view(['POST'])
def salvar_mensagem(request):
    if request.method == 'POST':
        serializer = MensagemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#------------------------------------------------Listar mensagens pelo id do aluno ordenado pela data------------------------------------------------#

@api_view(['GET'])
def listar_mensagens_por_aluno(request):
    if request.method == 'GET':
        id_aluno = request.GET.get('id', '')

        mensagens = Mensagem.objects.filter(id_aluno=id_aluno)

        serializer = MensagemSerializer(mensagens, many=True)

        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


#------------------------------------------------Listar todas as conversas------------------------------------------------#

@api_view(['GET'])
def listar_todos_alunos(request):
    if request.method == 'GET':
        # Obtém todas as mensagens que têm um aluno associado
        mensagens_com_alunos = Mensagem.objects.exclude(id_aluno=None)

        # Extrai os IDs únicos dos alunos
        ids_alunos_unicos = mensagens_com_alunos.values_list('id_aluno', flat=True).distinct()

        # Busca os dados dos alunos com base nos IDs únicos
        alunos = Aluno.objects.filter(id__in=ids_alunos_unicos)

        # Serializa os dados dos alunos
        serializer = AlunoSerializer(alunos, many=True)

        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def listar_informacoes_inicio(request):

# fazer depois com que essa rota retorne o número de conversas
# e número de conversas sobre determinado assunto
