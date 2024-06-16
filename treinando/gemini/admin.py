from django.contrib import admin
<<<<<<< HEAD
from .models import Pergunta, Usuario, Setor, Indicador, Pessoa, Relatorio, Script
from .serializers import PerguntaSerializer

# Register your models here.

class PerguntaAdmin(admin.ModelAdmin):
    readonly_fields = ('resposta', 'indicador')

class IndicadorAdmin(admin.ModelAdmin):
    readonly_fields = ('get_perguntas',)
    def get_perguntas(self, obj):
        perguntas = Pergunta.objects.filter(indicador=obj)
        serialized_data = []
        for pergunta in perguntas:
            serializer = PerguntaSerializer(pergunta)
            serialized_data.append(serializer.data)

        return serialized_data

admin.site.register(Pergunta, PerguntaAdmin)
admin.site.register(Usuario)
=======
from .models import Pergunta, Coordenador, Setor, Indicador, Pessoa, Relatorio, Script, Instituicao, Curso, Aluno, Mensagem, ControleBot, Conversa

# Register your models here.


from django.contrib import admin
from .models import Coordenador, Aluno
from .forms import CoordenadorAdminForm, AlunoAdminForm

class CoordenadorAdmin(admin.ModelAdmin):
    form = CoordenadorAdminForm
    list_display = ['nome', 'email', 'instituicao', 'curso', 'tipoAcesso']

class AlunoAdmin(admin.ModelAdmin):
    form = AlunoAdminForm
    list_display = ['nome', 'email', 'instituicao', 'curso', 'tipoAcesso']


admin.site.register(Coordenador, CoordenadorAdmin)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Pergunta)
>>>>>>> 02cec4173cdda5583b30c65fa00838d0ae4e6be1
admin.site.register(Setor)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(Pessoa)
admin.site.register(Relatorio)
admin.site.register(Script)
admin.site.register(Instituicao)
admin.site.register(Curso)
admin.site.register(Mensagem)
admin.site.register(ControleBot)
admin.site.register(Conversa)