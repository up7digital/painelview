from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
#-------------------------------------------------

from Administracao.views import ajax_carregar_unidades, ajax_carregar_servicos
from Painel_Web.views import personalizacao_css
from Painel_Web.Views.Home_PainelView import SelecionarPainelView, SelecionarSetor
from Painel_Web.Views.Painel_View import PainelView, painel_dados, painel_midias
from Painel_Web.Views.mercury import mercure_proxy

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("Administracao.urls")),

    #Rotas da Home
    path("", SelecionarPainelView.as_view(), name="painel_home"),
    path("selecionar/paineis-por-setor/", SelecionarSetor.as_view(), name="paineis_por_setor"),

    #Rotas dos Painéis
    path("painel/", PainelView.as_view(), name="exibir_painel"),
    path('painel-dados/', painel_dados, name="painel_dados"),
    path('painel-midias/', painel_midias, name="painel_midias"),
    path('mercure-proxy/<int:painel_id>/', mercure_proxy, name='mercure-proxy'),
    path('ajax/carregar-unidades/', ajax_carregar_unidades, name='ajax_carregar_unidades'),
    path('ajax/carregar-servicos/', ajax_carregar_servicos, name='ajax_carregar_servicos'),

    path('Personalizacao.css', personalizacao_css, name='personalizacao_css'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
