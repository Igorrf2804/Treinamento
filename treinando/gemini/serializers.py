from rest_framework import serializers
from .models import Pergunta, Coordenador, Script, Pessoa, Setor, Indicador, Relatorio, Aluno, Instituicao, Curso, Mensagem, ControleBot

class PerguntaSerializer(serializers.ModelSerializer):
    cont = serializers.IntegerField(required=False)

    class Meta:
        model = Pergunta
        fields = ['user', 'pergunta', 'cont']

class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = '__all__'
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        coordenador = Coordenador(
            nome=validated_data['nome'],
            email=validated_data['email'],
            instituicao=validated_data['instituicao'],
            curso=validated_data['curso'],
            tipoAcesso=validated_data['tipoAcesso'],
        )
        coordenador.set_password(validated_data['senha'])
        coordenador.save()
        return coordenador

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'usuario', 'senha', 'email']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        aluno = Aluno(
            nome=validated_data['nome'],
            email=validated_data['email'],
            instituicao=validated_data['instituicao'],
            curso=validated_data['curso'],
            tipoAcesso=validated_data['tipoAcesso'],
        )
        aluno.set_password(validated_data['senha'])
        aluno.save()
        return aluno

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

class MensagemSerializer(serializers.ModelSerializer):
    # gerar json dos modelos
    class Meta:
        model = Mensagem
        fields = '__all__'

class ControleBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControleBot
        fields = '__all__'
