from django.urls import path

from .Views.Conexoes import conexoes
from .Views.Conexoes_Detalhes import conexao_cadastro, conexao_detalhes
from .Views.Configuracoes_View import configuracoes
from .Views.Configuracao_Midias import configuracao_midias
from .Views.Gestao_Mideas import gestao_midias
from .Views.Gestao_Paineis import gestao_paineis
from .Views.Gestao_Setores import gestao_setores
from .Views.Gestao_Users import gestao_users
from .Views.login import login_view, logout_view
from .Views.Midea_Cadastro import midia_cadastro
from .Views.Midea_Detalhada import midia_detalhada
from .Views.Paineis_Detalhes import painel_cadastro, painel_detalhes
from .Views.Setores_Detalhes import setor_detalhes
from .Views.Setores_Cadastro import setor_cadastro
from .Views.Sons import gestao_sons, som_cadastro, som_excluir
from .Views.Users_Detalhes import user_detalhes
from .Views.Users_Cadastro import user_cadastro


app_name = "administracao"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("configuracoes/", configuracoes, name="configuracoes"),
    path(
        "configuracoes/usuarios/",
        gestao_users,
        name="gestao_users",
    ),
    path(
        "configuracoes/usuarios/novo/",
        user_cadastro,
        name="user_cadastro",
    ),
    path(
        "configuracoes/usuarios/<int:user_id>/",
        user_detalhes,
        name="user_detalhes",
    ),
    path(
        "configuracoes/setores/",
        gestao_setores,
        name="gestao_setores",
    ),
    path(
        "configuracoes/setores/novo/",
        setor_cadastro,
        name="setor_cadastro",
    ),
    path(
        "configuracoes/setores/<int:setor_id>/",
        setor_detalhes,
        name="setor_detalhes",
    ),
    path(
        "configuracoes/midias/",
        gestao_midias,
        name="gestao_midias",
    ),
    path(
        "configuracoes/midias/configuracao/",
        configuracao_midias,
        name="configuracao_midias",
    ),
    path(
        "configuracoes/midias/nova/",
        midia_cadastro,
        name="midia_cadastro",
    ),
    path(
        "configuracoes/midias/<int:midia_id>/",
        midia_detalhada,
        name="midia_detalhada",
    ),
    path(
        "configuracoes/midias/sons/",
        gestao_sons,
        name="gestao_sons",
    ),
    path(
        "configuracoes/midias/sons/novo/",
        som_cadastro,
        name="som_cadastro",
    ),
    path(
        "configuracoes/midias/sons/<int:som_id>/excluir/",
        som_excluir,
        name="som_excluir",
    ),
    path(
        "configuracoes/paineis/",
        gestao_paineis,
        name="gestao_paineis",
    ),
    path(
        "configuracoes/paineis/novo/",
        painel_cadastro,
        name="painel_cadastro",
    ),
    path(
        "configuracoes/paineis/<int:painel_id>/",
        painel_detalhes,
        name="painel_detalhes",
    ),
    path("configuracoes/conexoes/", conexoes, name="conexoes"),
    path(
        "configuracoes/conexoes/nova/",
        conexao_cadastro,
        name="conexao_cadastro",
    ),
    path(
        "configuracoes/conexoes/<int:conexao_id>/",
        conexao_detalhes,
        name="conexao_detalhes",
    ),
]
