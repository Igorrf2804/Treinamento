
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, UsuarioSerializer, PessoaSerializer, SetorSerializer, IndicadorSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Usuario, Pessoa, Setor, Indicador
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
import random

# Create your views here.

GOOGLE_API_KEY = "AIzaSyCLOvpQv7soejToFewHRrAWRaUkUVYQu3g"
# profissionais = [
#     {
#         "nome": "Roberto Medeira",
#         "profissao": "Coordenador do curso de informática",
#         "curso": "Informática",
#         "profissão": "Desenvolvedor"
#     }
# ]
codigos = [
    'd41d8cd98f00b204e9800998ecf8427e',
    '76df6506ab75a1e54e756a8ceaf63f03',
    '83e0699ed263e8e9bba48b587453a463'
]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
#---------------------------------------------INTEGRAÇÃO COM A GEMINI--------------------------------------------#


@api_view(['POST'])
@csrf_exempt
def create(request):
    dados = {
        "user": request.data.get('user'),
        "pergunta": request.data.get('pergunta')
    }
    serializer = PerguntaSerializer(data=dados)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    user = request.data.get('user')
    pergunta_txt = request.data.get('pergunta')
    pergunta = serializer.instance

    
    chat = model.start_chat(history=[])
    # Você é o Chatbot customizado da empresa CoordenaAgora, a partir de agora você irá responder perguntas
    # com x informações, e caso sejam mandados prompt que não sejam relacionados a área da educação você
    # irá responder: "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos", obs isso inclui
    # perguntas que não tem haver com problemas como histórico escolar, encaminhamento, agendamento, comunicar ao
    # coordenador etc

    scripts = Script.objects.all()
    serialized_data = []
    for script in scripts:
        serializer = ScriptsSerializer(script)
        serialized_data.append(serializer.data)
    profissionais = Usuario.objects.all()
    serializer_profissionais = []
    for profissional in profissionais:
        serializer = UsuarioSerializer(profissional)
        serializer_profissionais.append(serializer.data)

    descricoes = [item['descricao'] for item in serialized_data]
    descricoes += [item['usuario'] for item in serializer_profissionais]
    descricoes.append("""
    Se o aluno precisar de ajuda especializada ou o atendimento for longo, pergunte a ele se ele deseja ser/realizar:
    Encaminhamento: Retornar o código hash 'd41d8cd98f00b204e9800998ecf8427e' e o nome do profissional mais adequado para a situação.
    Agendamento: Retornar o código hash '76df6506ab75a1e54e756a8ceaf63f03' e o nome do profissional mais adequado para a situação.

    - Observações:

O chatbot não pode realizar as ações em nome do usuário, apenas orientá-lo.
O chatbot deve fornecer apenas informações que estejam disponíveis no site do CoordenaAgora.
O chatbot deve ser sempre educado e profissional ao interagir com o usuário.
O chatbot é capaz de realizar agendamentos e encaminhamentos.
O chatbot deve responder: 'Desculpe não possuo conhecimento disso, gostaria de ser encaminhado ou agendar uma reunião'. Caso não consiga atender as expectativas do aluno.
O chatbot deve perguntar se o aluno quer marcar uma reunião ou ser encaminhado se o aluno não conseguir fazer algo com as instruções do chatbot.
O chatbot não pode mandar links ao usuário, caso ele necessita realizar encaminhamento ou agendamento ao aluno, isso sera feito pelo backend após receber o hash e o nome do profissional selecionado.
O chatbot nunca deve fazer um encaminhamento ou agendamento sem antes perguntar ao aluno se ele deseja ser encaminhado ou agendar uma reunião.
    """)

    chat.send_message(descricoes)
    # chat.send_message(descricoes)
    resposta = chat.send_message(pergunta_txt)
    cont = request.data.get('cont')
    if resposta.candidates[0].content.parts[
        0].text != "" and codigos[2] not in \
        resposta.candidates[0].content.parts[0].text:
        pergunta.resposta = resposta.candidates[0].content.parts[0].text
        if cont < 8:
            if codigos[0] in pergunta.resposta.lower():
                for profissional in serializer_profissionais:
                    print(profissional)
                    if profissional['usuario'] in pergunta.resposta:
                        email = profissional['email']
                        if Usuario.objects.filter(email=email).exists() and Usuario.objects.filter(usuario = request.data.get('user')).exists():

                            u = UsuarioSerializer(Usuario.objects.filter(usuario = request.data.get('user')))

                            tema = 'Encaminhamento realizado para você para os dias x/y/2024'
                            msg = f'Um encaminhamento foi realizado para você para o atendimento do usuário {request.data.get("user")} nos dias x/y/2024, por favor entre em contato quando possível'
                            remetente = "ads.senac.tcs@gmail.com"
                            send_mail(tema, msg, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
                    
                            tema = f'Encaminhamento realizado com sucesso.'
                            msg = f'Você foi encaminhado durante o dia x/y/2024 para o profissional {profissional["usuario"]}, por favor aguarde um pouco para ser atendido'
                            remetente = "ads.senac.tcs@gmail.com"
                            send_mail(tema, msg, remetente, recipient_list=[u.data['email'],'ads.senac.tcs@gmail.com'])

                            classificar_conversa(chat, request.data.get('user'))
                            return Response({'mensagem': "O encaminhamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)

                return Response({'mensagem': 'Ocorreu um erro ao realizar o encaminhamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)
                
            if codigos[1] in pergunta.resposta.lower():
                for profissional in serializer_profissionais:
                    if profissional['usuario'] in pergunta.resposta:
                        email = profissional['email']
                        if Usuario.objects.filter(email=email).exists() and Usuario.objects.filter(usuario = request.data.get('user')).exists():

                            u = UsuarioSerializer(Usuario.objects.filter(usuario = request.data.get('user')))

                            tema = 'Reunião agendada para você para os dias x/y/2024'
                            msg = f'Um agendamento foi realizado para você para o atendimento do usuário {request.data.get("user")} no dia x/y/2024 as 18:00'
                            remetente = "ads.senac.tcs@gmail.com"
                            send_mail(tema, msg, remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])
                    
                            tema = f'Reunião agendada com sucesso.'
                            msg = f'Você agendou com sucesso uma reunião para o dia x/y/2024 as 17:00 com o profissional {profissional["usuario"]}'
                            remetente = "ads.senac.tcs@gmail.com"
                            send_mail(tema, msg, remetente, recipient_list=[u.data['email'],'ads.senac.tcs@gmail.com'])

                            classificar_conversa(chat, request.data.get('user'))
                            return Response({'mensagem': "O agendamento foi realizado com sucesso!"}, status=status.HTTP_201_CREATED)

                return Response({'mensagem': 'Ocorreu um erro ao realizar o agendamento, peço desculpas'}, status = status.HTTP_400_BAD_REQUEST)

            return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)
        else:
            return Response({'mensagem': 'Peço desculpas, creio que não conseguirei atender as suas expectativas, gostaria que eu o encaminhasse a algum profissional mais qualificado ou agende uma reunião com alguem para você?'}, status = status.HTTP_200_OK)

    return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)

#---------------------------------------------REDEFINIR SENHA--------------------------------------------#

def classificar_conversa(chat: genai.ChatSession, usuario):
    indicadores = Indicador.objects.all()
    serializer_indicadores = []
    for indicador in indicadores:
        serializer = IndicadorSerializer(indicador)
        serializer_indicadores.append(serializer.data)
    
    msg = 'Gemini, classifique nossa conversa com um dos seguintes indicadores e retorne ele para mim: ' + ', '.join(serializer_indicadores.nome)
    dados = {
        "user": usuario,
        "pergunta": msg
    }
    pergunta_serializer = PerguntaSerializer(data=request.data)
    pergunta_serializer.is_valid(raise_exception=True)
    pergunta_serializer.save()
    resposta = chat.send_message(msg)
    pergunta_serializer.resposta = resposta.candidates[0].content.parts[0].text
    for indicador in serializer_indicadores:
        if indicador.nome in resposta:
            pergunta_serializer.indicador = indicador.id
            return True
    return False


@api_view(['POST'])
def redefinir_senha(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if (Usuario.objects.filter(email=email).exists()):
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
    send_mail(assunto, mensagem,remetente, recipient_list=[email,'ads.senac.tcs@gmail.com'])

@api_view(['PUT'])
def alterar_senha(request):
    if request.method == 'PUT':
        email = request.data.get('email')
        senha = request.data.get('senha')  # Obtenha a senha dos dados da solicitação

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response("Usuário não encontrado", status=status.HTTP_404_NOT_FOUND)

        dados = {'usuario': usuario.usuario, 'senha': senha}
        serializer = UsuarioSerializer(usuario, data=dados)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Método de solicitação inválido", status=status.HTTP_405_METHOD_NOT_ALLOWED)


#-------------------------------------------------LOGIN------------------------------------------------#

class UsuarioViewSet(viewsets.ViewSet):
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        usuario = request.data.get("usuario")
        senha = request.data.get("senha")
        if (Usuario.objects.filter(usuario=usuario, senha=senha).exists()):
            return Response({'resultado': True}, status=status.HTTP_200_OK)
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

        serializer = SetorSerializer(scripts, many=True)  # Serialize the object data into json (Has a 'many' parameter cause it's a queryset)

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


# @api_view(['GET'])
# def listar_informacoes_inicio(request):

    # fazer depois com que essa rota retorne o número de conversas
    # e número de conversas sobre determinado assunto

