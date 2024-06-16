from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, CoordenadorSerializer, PessoaSerializer, SetorSerializer, \
    IndicadorSerializer, InstituicaoSerializer, CursoSerializer, AlunoSerializer, MensagemSerializer, ControleBotSerializer, ConversaSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta, Script, Coordenador, Pessoa, Setor, Indicador, Instituicao, Curso, Aluno, Mensagem, ControleBot, Conversa
import google.generativeai as genai
from .serializers import ScriptsSerializer
from rest_framework.decorators import api_view, action
import random
from datetime import datetime, timedelta
from django.utils import timezone as django_timezone
from django.core.exceptions import ObjectDoesNotExist
import psycopg2
import reportlab

# Create your views here.


# chat/views.py
from django.shortcuts import render


def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})



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
    historico = request.data.get('historico')
    id_aluno = request.data.get('id_aluno')

    formatted_messages = []

    role_map = {
        'aluno': 'user',
        'bot': 'model'
    }

    for hist in historico:
        role = role_map.get(hist['quem_enviou'], 'user')
        parts = hist['texto_mensagem']
        formatted_messages.append({
            'role': role,
            'parts': parts
        })

    ultima_mensagem = Mensagem.objects.filter(id_aluno=id_aluno).order_by('id').reverse().first();
    mensagem_count = Mensagem.objects.filter(id_conversa_id=ultima_mensagem.id_conversa, quem_enviou='aluno').count()
    controle_bot = get_controle_bot(id_aluno)

    if(controle_bot.bot_pode_responder and mensagem_count >= 6):
        return Response({'mensagem': 'A conversa foi finalizada'}, status=status.HTTP_201_CREATED)
    else:
        pergunta = serializer.instance

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=formatted_messages)

        scripts = Script.objects.all()
        serialized_data = []
        if len(scripts) > 0:
            for script in scripts:
                serializer = ScriptsSerializer(script)
                serialized_data.append(serializer.data)
        else:
            return Response({'mensagem': 'Não existem scripts cadastrados'}, status=status.HTTP_400_BAD_REQUEST)

        descricoes = [item['descricao'] for item in serialized_data]
        instrucao = 'Você deve responder a mensagem: "' + pergunta_txt + '" com base nas seguintes instruções: ' + ', '.join(descricoes) + '. Caso a mensagem não corresponda a nenhuma instrução você deve responder: "Desculpe não consigo responder essa pergunta."'
        print(instrucao)
        resposta = chat.send_message(instrucao)

        if resposta.candidates[0].content.parts[
            0].text != "" and "desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" not in \
                resposta.candidates[0].content.parts[0].text:
            pergunta.resposta = resposta.candidates[0].content.parts[0].text
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
        coordenador = Coordenador.objects.filter(email=email).first()
        if coordenador and coordenador.check_senha(senha):
            serializer = CoordenadorSerializer(coordenador)
            return Response({'resultado': True, 'dadosDoUsuario': serializer.data}, status=status.HTTP_200_OK)

        # Verifica Aluno
        aluno = Aluno.objects.filter(email=email).first()
        if aluno and aluno.check_senha(senha):
            serializer = AlunoSerializer(aluno)
            return Response({'resultado': True, 'dadosDoUsuario': serializer.data}, status=status.HTTP_200_OK)

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
        setores = Setor.objects.all()  # Get all objects in User's database (It returns a queryset)

        serializer = SetorSerializer(setores,
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
        id_aluno = request.data.get('id_aluno')
        id_coordenador = request.data.get('id_coordenador')
        ultima_mensagem = Mensagem.objects.filter(id_aluno=id_aluno).order_by('id').reverse().first();

    if ultima_mensagem:
        now = django_timezone.now()
        hora_ultima_mensagem = ultima_mensagem.data_hora
        diferenca = now - hora_ultima_mensagem

        tres_horas = timedelta(hours=3)
        # tres_horas = timedelta(seconds=3)
        # tres_horas = timedelta(minutes=3)

        if diferenca > tres_horas:
            # se passou mais de 3 horas desde a última mensagem a conversa deve ser finalizada:
            if(id_aluno):
                user = id_aluno
            else:
                user = id_coordenador

            formatted_messages = get_historico_conversa(ultima_mensagem)

            request.data['id_conversa'] = ultima_mensagem.id_conversa.id
            classificar_conversa(formatted_messages, user, ultima_mensagem.id_conversa)
            request.data['id_conversa'] = adicionar_conversa()
            serializer = salvar_nova_mensagem(request)
            if ultima_mensagem.quem_enviou == 'aluno':
                verificar_encaminhamento_agendamento(request.data['id_conversa'], id_aluno, ultima_mensagem)
            return Response(status=status.HTTP_201_CREATED)
        elif (ultima_mensagem.id_conversa == None):
            #se não tem uma conversa associada na última mensagem
            request.data['id_conversa'] = adicionar_conversa()
            serializer = salvar_nova_mensagem(request)
            if ultima_mensagem.quem_enviou == 'aluno':
                verificar_encaminhamento_agendamento(request.data['id_conversa'], id_aluno, ultima_mensagem)
            if(serializer):
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            #se não passou mais de três horas desde a última mensagem do aluno
            status_conversa = verificar_status_conversa(ultima_mensagem.id_conversa.id)
            if(status_conversa == True):
                #se a conversa ainda está ativa deve salvar a mensagem com o mesmo id da conversa
                request.data['id_conversa'] = ultima_mensagem.id_conversa.id
                serializer = salvar_nova_mensagem(request)
                if ultima_mensagem.quem_enviou == 'aluno':
                    verificar_encaminhamento_agendamento(request.data['id_conversa'], id_aluno, ultima_mensagem)
                return Response(status=status.HTTP_201_CREATED)
            else:
                #se a conversa não está ativa deve iniciar uma nova e a mensagem é salva com esse id da conversa nova
                request.data['id_conversa'] = adicionar_conversa()
                serializer = salvar_nova_mensagem(request)
                if ultima_mensagem.quem_enviou == 'aluno':
                    verificar_encaminhamento_agendamento(request.data['id_conversa'], id_aluno, ultima_mensagem)
                return Response(status=status.HTTP_201_CREATED)
    else:
        #se não tem uma última mensagem (se o aluno não enviou nenhuma mensagem ainda)
        request.data['id_conversa'] = adicionar_conversa()
        serializer = salvar_nova_mensagem(request)
        return Response(status=status.HTTP_201_CREATED)

def salvar_nova_mensagem(request):
    serializer = MensagemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return serializer

def verificar_status_conversa(id_conversa):
    conversa = Conversa.objects.get(id=id_conversa)
    return conversa.status

def get_historico_conversa(ultima_mensagem):
    historico_conversa = Mensagem.objects.filter(id_conversa=ultima_mensagem.id_conversa).order_by('id');

    formatted_messages = []

    role_map = {
        'aluno': 'user',
        'bot': 'model'
    }

    for message in historico_conversa:
        role = role_map.get(message.quem_enviou, 'user')
        parts = message.texto_mensagem
        formatted_messages.append({
            'role': role,
            'parts': parts
        })

    return formatted_messages

def adicionar_conversa():
    data = {
        'status': True
    }
    serializer = ConversaSerializer(data = data)
    if serializer.is_valid():
        conversa = serializer.save();
        return conversa.id
    return None

def verificar_encaminhamento_agendamento(id_conversa, id_aluno, ultima_mensagem):
    mensagem_count = Mensagem.objects.filter(id_conversa_id=id_conversa, quem_enviou='aluno').count()
    controle_bot = get_controle_bot(id_aluno)

    if(controle_bot.bot_pode_responder and mensagem_count >= 6):
        historico_conversa = get_historico_conversa(ultima_mensagem)

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=historico_conversa)
        classificacao = chat.send_message("Com base na nossa conversa você deve realizar um encaminhamento " +
                                     "ou agendamento. Utilize as informações abaixo para fazer a classificação de encaminhar " +
                                     "ou agendar: Agendamento: Você deve avaliar as mensagens enviadas e verificar se elas tem " +
                                     "relação com: planejamento e problemas acadêmicos: Escolha de disciplinas e planejamento de cursos; " +
                                     "Dúvidas sobre requisitos de graduação e pré-requisitos de disciplinas; Orientação sobre mudanças de " +
                                     "curso ou transferência entre programas, orientação profissional: Informações sobre estágios, oportunidades "+
                                     "de emprego e carreiras relacionadas ao curso; Networking e eventos de carreira; problemas " +
                                     "com professores ou colegas: Conflitos ou problemas de comunicação com professores; Questões sobre a metodologia " +
                                     "de ensino ou avaliação; e casos especiais: Trancamento do curso. O agendamento é quando o coordenador " +
                                     "recebe uma demanda. Você não deve classificar como agendamento caso as mensagens não " +
                                     "tiverem relação com os itens citados. Já o encaminhamento é quando o assunto não tem " +
                                     "relação com o coordenador de curso, os assuntos que recebem a classificação encaminhamento são: " +
                                     "questões administrativas, biblioteca, infraestrutura e assuntos acadêmicos gerais. O encaminhamento " +
                                     "é quando a assunto é relacionado a outros setores da instituição de ensino superior que não seja " +
                                     "a coordenação de curso. Você não deve classificar como encaminhamento caso as mensagens não " +
                                     "tiverem relação com os itens citados. Você precisa retornar apenas uma palavra: encaminhamento ou agendamento")
        print(classificacao.text)

        role_map = {
            'user': 'aluno',
            'model': 'chatbot'
        }

        # Função para formatar a lista em uma string
        def format_dialogue(dialogue):
            formatted_str = ""
            for entry in dialogue:
                role = role_map.get(entry['role'], entry['role'])
                parts = entry['parts']
                formatted_str += f"{role}: {parts}\n"
            return formatted_str
        conversa_formatada = format_dialogue(historico_conversa)

        if (classificacao.text.lower() == 'encaminhamento'):
            setores = Setor.objects.all()
            serializer_setores = []
            for setor in setores:
                serializer = SetorSerializer(setor)
                serializer_setores.append(serializer.data)


            # instrucao = "Com base no histórico, você deve classificar o setor que o assunto da conversa mais se encaixa. O setores podem ser: " + " , ".join([item['nome'] for item in serializer_setores])



            instrucao = "Com base na seguinte conversa: \n " + conversa_formatada + "\n você deve classificar o setor que o assunto da conversa mais se encaixa. O setores podem ser: financeiro: relacionados a segunda via de boletos; secretaria: relacionados a atestado de matrícula, histórico acadêmico e validação de horas complementares; biblioteca: relacionado ao aluguel de livros acadêmicos. Você deve retornar apenas o nome do setor em letras minúsculas. Você não deve retornar um setor que não seja um desses enviados."
            setor = model.generate_content(instrucao)

            for setor_serializer in serializer_setores:
                if setor_serializer['nome'].strip().lower() == setor.text.strip().lower():
                    pessoas_ids = setor_serializer['pessoas']
                    pessoas_setor = Pessoa.objects.filter(id__in=pessoas_ids)
                    for pessoa in pessoas_setor:

                        try:
                            aluno = Aluno.objects.get(id=id_aluno)
                        except ObjectDoesNotExist:
                            print(f'Aluno com id {id_aluno} não encontrado.')
                            return


                        assunto = 'Encaminhamento realizado'
                        msg = f'Um encaminhamento foi realizado para o atendimento do aluno abaixo: \n\nAluno:{aluno.nome} \nEmail: {aluno.email} \n\nPor favor, entre em contato assim que possível.\n \n{conversa_formatada}'
                        remetente = "ads.senac.tcs@gmail.com"
                        recipient_list = [pessoa.email, 'ads.senac.tcs@gmail.com', aluno.email]

                        # Envia o email
                        send_mail(assunto, msg, remetente, recipient_list)
                        classificar_conversa(historico_conversa, id_aluno, ultima_mensagem.id_conversa)
                        return Response({'mensagem': "Foi realizado um encaminhamento para o setor responsável, você pode realizar o acompanhamento através do email."}, status=status.HTTP_201_CREATED)

                    return
        else:
            if id_aluno is None:
                return Response({"error": "id_aluno não fornecido"}, status=status.HTTP_400_BAD_REQUEST)

            aluno = Aluno.objects.get(id=id_aluno)
            coordenador = Coordenador.objects.filter(instituicao=aluno.instituicao_id, curso=aluno.curso_id).first()

            if coordenador:
                assunto = 'Agendamento realizado'
                msg = f'Um agendamento foi realizado para o atendimento do aluno abaixo: \n\nAluno:{aluno.nome} \nEmail: {aluno.email} \n\nPor favor, entre em contato assim que possível.\n \n{conversa_formatada}'
                remetente = "ads.senac.tcs@gmail.com"
                send_mail(assunto, msg, remetente, recipient_list=[coordenador.email,'ads.senac.tcs@gmail.com', aluno.email])
                classificar_conversa(historico_conversa, id_aluno, ultima_mensagem.id_conversa)
                return Response({'mensagem': "Foi realizado um agendamento para o coordenador do seu curso, você pode realizar o acompanhamento através do email."}, status=status.HTTP_201_CREATED)





#------------------------------------------------Listar mensagens pelo id do aluno ordenado pela data------------------------------------------------#

@api_view(['GET'])
def listar_mensagens_por_aluno(request):
    if request.method == 'GET':
        id_aluno = request.GET.get('id', '')

        mensagens = Mensagem.objects.filter(id_aluno=id_aluno).order_by('id')

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



#------------------------------------------------Mudar status bot------------------------------------------------#
@api_view(['POST'])
def mudar_status_bot(request):
    if request.method == 'POST':
        status_bot = request.data.get('status')
        id_aluno = request.data.get('id_aluno')

        controle_bot = ControleBot.objects.filter(id_aluno=id_aluno).first()
        if controle_bot:
            dados = {'bot_pode_responder': status_bot, 'id_aluno': controle_bot.id_aluno.id}
            serializer = ControleBotSerializer(controle_bot, data=dados)
        else:
            dados = {'bot_pode_responder': status_bot, 'id_aluno': id_aluno}
            serializer = ControleBotSerializer(data=dados)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verificar_status_bot(request):
    if request.method == 'GET':
        id_aluno = request.query_params.get('id_aluno')
        controle_bot = get_controle_bot(id_aluno)
        if controle_bot:
            serializer = ControleBotSerializer(controle_bot)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "ControleBot não encontrado para o id_aluno fornecido"}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)

def get_controle_bot(id_aluno):
    if id_aluno is None:
        return Response({"error": "id_aluno não fornecido"}, status=status.HTTP_400_BAD_REQUEST)

    controle_bot = ControleBot.objects.filter(id_aluno=id_aluno).first()
    return controle_bot


def classificar_conversa(historico, usuario, id_conversa):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=historico)

    indicadores = Indicador.objects.all()
    serializer_indicadores = []
    for indicador in indicadores:
        serializer = IndicadorSerializer(indicador)
        serializer_indicadores.append(serializer.data)

    msg = 'Gemini, classifique nossa conversa com um dos seguintes indicadores e retorne ele para mim. Não retorne nenhuma outra informação além do indicador e deve ser apenas 1 indicador, aquele que mais se encaixa. Os indicadores podem ser: ' + ', '.join([item['nome'] for item in serializer_indicadores])
    print(msg)
    dados = {
        "user": usuario,
        "pergunta": msg
    }
    pergunta = Pergunta(
        user = usuario,
        pergunta = msg
    )
    pergunta.usuario = dados['user'],
    resposta = chat.send_message(msg)
    pergunta.resposta = resposta.candidates[0].content.parts[0].text



    for indicador in serializer_indicadores:
        if indicador['nome'].lower() in pergunta.resposta.lower():

            serializer_indicador = Indicador.objects.get(id = indicador['id'])
            # print(' pergunta.indicador------------------',  indicador)
            # pergunta.indicador = indicador
            # pergunta.save()

            try:
                conversa = Conversa.objects.get(id=id_conversa.id)
            except Conversa.DoesNotExist:
                conversa = None
                print("Conversa com o id fornecido não existe.")

            if conversa:
                conversa.status = False
                conversa.id_indicador = serializer_indicador

                serializer = ConversaSerializer(conversa, data={
                    'status': conversa.status,
                    'id_indicador': conversa.id_indicador.id,
                    'outros_campos': 'valores'
                }, partial=True)

                if serializer.is_valid():
                    serializer.save()
                else:
                    print(serializer.errors)

            return True

    return False

def strToDatetime(data):
    formato_string = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(data, formato_string)

@api_view(['POST'])
def gerar_relatorio(request):
    try:
        coordenador_id = request.data.get('coordenador_id')
        indicadores = request.data.get('indicadores')
        data_inicial = strToDatetime(request.data.get('data_inicial'))
        data_final = strToDatetime(request.data.get('data_final'))
    except:
        return Response({"error": "Erro ao obter dados da requisição"}, status=status.HTTP_400_BAD_REQUEST)
    
    teste = Conversa.objects.all()
    print(type(teste[0].data_hora))
    count = {}
    for indicador in indicadores:
        count[indicador['nome']] = Conversa.objects.filter(data_hora__range=[data_inicial, data_final], id_indicador = indicador['id']).count()
    print(count)
    conversas = ConversaSerializer(Conversa.objects.filter(data_hora__range=[data_inicial, data_final], id_indicador = indicador ), many=True)
    


    return Response(status=status.HTTP_400_BAD_REQUEST)
    print(conversas[0].id_indicador)
    # query = f"select * from gemini_mensagem where data_hora between {data_inicial} and {data_final}"
    # mensagens = Mensagem.objects.filter(data_hora__range=[data_inicial, data_final])
    # mensagens = MensagemSerializer(mensagens, many=True)

    # conversas = []
    # count = {}
    # total = 0
    # for indicador in indicadores:
    #     indicador = IndicadorSerializer(indicador)
    #     count[indicador.data['nome']] = 0
    #     for mensagem in mensagens.data:
    #         conversa = ConversaSerializer(Conversa.objects.filter(id=mensagem['id_conversa']))
    #         print(conversa.data)
    #         if conversa.data not in conversas:
    #             conversas += conversa.data
    #             total += 1
    
    # print(count)
    # for conversa in conversas:
    #     for indicador in indicadores:
    #         print(conversa)
    #         if conversa['id_indicador'] == indicador.id:
    #             count[indicador.nome] += 1
    
    # print(conversa)