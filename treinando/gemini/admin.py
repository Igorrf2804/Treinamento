from django.contrib import admin
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
admin.site.register(Setor)
admin.site.register(Indicador)
admin.site.register(Pessoa)
admin.site.register(Relatorio)
admin.site.register(Script)
admin.site.register(Instituicao)
admin.site.register(Curso)
admin.site.register(Mensagem)
admin.site.register(ControleBot)
admin.site.register(Conversa)