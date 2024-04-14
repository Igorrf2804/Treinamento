from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PerguntaSerializer, UsuarioSerializer, ScriptSerializer, PessoaSerializer, SetorSerializer, IndicadorSerializer, RelatorioSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta
import google.generativeai as genai
import requests
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
        if resposta.candidates[0].content.parts[0].text != "" and ("desculpe, sou um bot usado apenas para a resolução de problemas acadêmicos" in resposta.candidates[0].content.parts[0].text):
            print(resposta.candidates[0].content.parts[0].text)
            pergunta.resposta = resposta.candidates[0].content.parts[0].text
            return Response({'mensagem': resposta.candidates[0].content.parts[0].text}, status=status.HTTP_201_CREATED)
            #return Response({'mensagem': 'deu ruim'})
            
        return Response({'mensagem': 'Erro ao fazer a pergunta'}, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ModelViewSet):
    #queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class ScriptViewSet(viewsets.ModelViewSet):
    #queryset = Script.objects.all()
    serializer_class = ScriptSerializer

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