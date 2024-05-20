from django.contrib import admin
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
admin.site.register(Setor)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(Pessoa)
admin.site.register(Relatorio)
admin.site.register(Script)