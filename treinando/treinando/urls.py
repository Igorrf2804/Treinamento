
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# from treinando.gemini.views import PerguntaViewSet, UsuarioViewSet

from gemini.views import  UsuarioViewSet



router = routers.DefaultRouter()
# router.register(r'perguntas', PerguntaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    path('login/', UsuarioViewSet.as_view({'post' : 'login'})),

    # path('redefinir-senha/', UsuarioViewSet.as_view({'post' : 'redefinir_senha'})),


    path('api/', include('gemini.urls'), name='gemini_urls'),

]
