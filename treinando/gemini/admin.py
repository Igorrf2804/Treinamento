from django.contrib import admin
from .models import Pergunta, Usuario, Setor, Indicador, Pessoa, Relatorio, Script

# Register your models here.

admin.site.register(Pergunta)
admin.site.register(Usuario)
admin.site.register(Setor)
admin.site.register(Indicador)
admin.site.register(Pessoa)
admin.site.register(Relatorio)
admin.site.register(Script)