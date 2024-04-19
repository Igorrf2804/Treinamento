
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from gemini.views import PerguntaViewSet, UsuarioViewSet

router = routers.DefaultRouter()
router.register(r'perguntas', PerguntaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    path('login/', UsuarioViewSet.as_view({'post' : 'login'})),
    path('recuperarSenha/', UsuarioViewSet.as_view({'post' : 'recuperar_senha'})),

    path('api/', include('gemini.urls'), name='gemini_urls'),

]
