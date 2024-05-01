from rest_framework import serializers
from .models import Pergunta, Coordenador, Script, Pessoa, Setor, Indicador, Relatorio, Aluno, Instituicao, Curso

class PerguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pergunta
        fields = ['user', 'pergunta']

class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = ['id', 'usuario', 'senha']

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = '__all__'


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

class InstituicaoSerializer(serializers.ModelSerializer):
    # gerar json dos modelos
    class Meta:
        model = Instituicao
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    # gerar json dos modelos
    class Meta:
        model = Curso
        fields = '__all__'
