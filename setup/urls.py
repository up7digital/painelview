from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
#-------------------------------------------------

from Administracao.views import ajax_carregar_unidades, ajax_carregar_servicos
from Painel_Web.views import SelecionarPainelView, PainelView, mercure_proxy, painel_dados

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", SelecionarPainelView.as_view(), name="painel_home"),
    path("painel/", PainelView.as_view(), name="exibir_painel"),
    path('painel-dados/', painel_dados, name="painel_dados"),
    path('mercure-proxy/<int:painel_id>/', mercure_proxy, name='mercure-proxy'),
    path('ajax/carregar-unidades/', ajax_carregar_unidades, name='ajax_carregar_unidades'),
    path('ajax/carregar-servicos/', ajax_carregar_servicos, name='ajax_carregar_servicos'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
