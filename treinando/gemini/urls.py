from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    # path('', views.get_users, name='get_all_users'),
    path('scripts', views.listar_scripts, name='listar_todos_scripts'),
    path('cadastrar-script', views.cadastrar_script, name='cadastrar_script'),
    path('editar-script/<int:id>', views.editar_script, name='editar_script'),
    path('pessoas', views.listar_pessoas, name='listar_pessoas'),
    path('cadastrar-pessoa', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('indicadores', views.listar_indicadores, name='listar_indicadores'),
    path('cadastrar-indicador', views.cadastrar_indicador, name='cadastrar_indicador'),
    # path('user/<str:nick>', views.get_by_nick),
    # path('data/', views.user_manager)
]
