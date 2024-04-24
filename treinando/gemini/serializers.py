from rest_framework import serializers
from .models import Pergunta, Usuario, Script, Pessoa, Setor, Indicador, Relatorio

class PerguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pergunta
        fields = ['user', 'pergunta']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'usuario', 'senha']

class ScriptsSerializer(serializers.ModelSerializer):
    # gerar json dos modelos
    class Meta:
        model = Script
        fields = '__all__'

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['id', 'nome', 'email']

class SetorSerializer(serializers.ModelSerializer):
    pessoas = serializers.PrimaryKeyRelatedField(queryset = Pessoa.objects.all(), many=True)
    class Meta:
        model = Setor
        fields = ['id', 'nome', 'pessoas']
        depth = 1 

class IndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicador
        fields = ['id', 'nome', 'descricao']

class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ['data_inicial', 'data_final', 'indicadores']
        depth = 1
    
    
