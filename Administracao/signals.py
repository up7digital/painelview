from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import (
    AudioCampainha, MidiaPainel, tb_Conexoes, tb_Painel, tb_Setores, ConfigPainel,
)


PERMISSOES = (
    ("gerenciar_conexao", "Gerenciar conexões", tb_Conexoes),
    ("gerenciar_paineis", "Gerenciar painéis", tb_Painel),
    ("acesso_mideas", "Acessar Gestão de Mídias", MidiaPainel),
    ("gerenciar_mideas", "Gerenciar mídias", MidiaPainel),
    ("gerenciar_sons", "Gerenciar sons", AudioCampainha),
    ("gerenciar_config_mideas", "Gerenciar sons", ConfigPainel),
    ("gerenciar_setores", "Gerenciar setores", tb_Setores),
    ("acesso_usuarios", "Acessar gestão de usuários", get_user_model()),
    ("visualizar_usuarios", "Visualizar usuários", get_user_model()),
    ("cadastrar_usuarios", "Cadastrar usuários", get_user_model()),
    ("editar_usuarios", "Editar usuários", get_user_model()),
)


@receiver(
    post_migrate,
    dispatch_uid="administracao_configurar_grupos_e_permissoes",
)
def configurar_grupos_e_permissoes(sender, **kwargs):
    """Cria e sincroniza os grupos e permissões após as migrações."""
    if sender.name != "Administracao":
        return

    permissoes = {}

    with transaction.atomic():
        for codename, nome, model in PERMISSOES:
            content_type = ContentType.objects.get_for_model(model)
            permissao, _ = Permission.objects.update_or_create(
                content_type=content_type,
                codename=codename,
                defaults={"name": nome},
            )
            permissoes[codename] = permissao

        grupo_admin, _ = Group.objects.get_or_create(name="Admin")
        grupo_admin.permissions.set(permissoes.values())

        grupo_social_media, _ = Group.objects.get_or_create(
            name="Social media"
        )
        grupo_social_media.permissions.set(
            [
                permissoes["acesso_mideas"],
                permissoes["gerenciar_mideas"],
                permissoes["gerenciar_config_mideas"],
            ]
        )
