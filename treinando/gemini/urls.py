from django.contrib import admin
from django.urls import path, include

from . import views
from .views import TelaInicialViewSet, RelatorioViewSet

urlpatterns = [
    # path('', views.get_users, name='get_all_users'),
    path('scripts', views.listar_scripts, name='listar_todos_scripts'),
    path('cadastrar-script', views.cadastrar_script, name='cadastrar_script'),
    path('editar-script/<int:id>', views.editar_script, name='editar_script'),
    path('excluir-script/<int:id>', views.excluir_script, name='excluir_script'),

    path('pessoas', views.listar_pessoas, name='listar_pessoas'),
    path('cadastrar-pessoa', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('editar-pessoa/<int:id>', views.editar_pessoa, name='editar_pessoa'),
    path('excluir-pessoa/<int:id>', views.excluir_pessoa, name='excluir_pessoa'),
    # fazer rota que busca pessoas pelo id

    path('indicadores', views.listar_indicadores, name='listar_indicadores'),
    path('cadastrar-indicador', views.cadastrar_indicador, name='cadastrar_indicador'),
    path('editar-indicador/<int:id>', views.editar_indicador, name='editar_indicador'),
    path('excluir-indicador/<int:id>', views.excluir_indicador, name='excluir_indicador'),

    path('inicio/', TelaInicialViewSet.as_view({'get' : 'listarDados'})),

    path('visualizar-setores/', views.visualizar_setores, name='visualizar-setores'),
    path('cadastrar-setores', views.cadastrar_setores, name='cadastrar-setores'),
    path('editar-setores/<int:id>', views.editar_setores, name='editar-setores'),
    path('excluir-setores/<int:id>', views.excluir_setores, name='excluir-setores'),

    path('relatorio', RelatorioViewSet.as_view({'post' : 'enviar-relatorio'}))
    # path('user/<str:nick>', views.get_by_nick),
    # path('data/', views.user_manager)
]
