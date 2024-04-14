from rest_framework import serializers
from .models import Pergunta, Usuario, Script, Pessoa, Setor, Indicador, Relatorio

class PerguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pergunta
        fields = ['user', 'pergunta']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['usuario', 'senha']

class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = ['nome', 'descricao']

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['nome', 'email']

class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = ['nome', 'pessoas']

class IndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicador
        fields = ['nome', 'descricao']

class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ['data_inicial', 'data_final', 'indicadores']
