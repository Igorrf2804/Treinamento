"""
URL configuration for treinando project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from gemini.views import TelaInicialViewSet, PerguntaViewSet, UsuarioViewSet, PessoaViewSet, SetorViewSet, IndicadorViewSet, RelatorioViewSet

router = routers.DefaultRouter()
router.register(r'perguntas', PerguntaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    path('login/', UsuarioViewSet.as_view({'post' : 'login'})),
    path('recuperarSenha/', UsuarioViewSet.as_view({'post' : 'recuperar_senha'})),

    path('api/', include('gemini.urls'), name='gemini_urls'),
    path('inicio/', TelaInicialViewSet.as_view({'get' : 'listarDados'})),

    path('visualizarSetores/', SetorViewSet.as_view({'get' : 'visualizarSetores'})),
    path('cadastrarSetores/', SetorViewSet.as_view({'post' : 'cadastrarSetores'})),
    path('editarSetores/', SetorViewSet.as_view({'put' : 'editarSetores'})),
    path('excluirSetores/', SetorViewSet.as_view({'delete' : 'excluirSetores'})),
    
    path('relatorio/', RelatorioViewSet.as_view({'post' : 'enviarRelatorio'}))
]
