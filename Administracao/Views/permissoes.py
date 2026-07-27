from Administracao.models import tb_Setores


def usuario_eh_admin(usuario):
    """Informa se o usuário pode acessar todos os setores."""
    return (
        usuario.is_superuser
        or usuario.groups.filter(name="Admin").exists()
    )


def setores_do_usuario(usuario):
    """Retorna todos os setores vinculados diretamente ao usuário."""
    return tb_Setores.objects.filter(
        usuarios_vinculados__usuario=usuario,
    ).order_by("nome_setor").distinct()


def setores_permitidos(usuario):
    """Retorna os setores que o usuário pode administrar."""
    if usuario_eh_admin(usuario):
        return tb_Setores.objects.order_by("nome_setor")

    return setores_do_usuario(usuario)


def setor_do_usuario(usuario):
    """Mantém compatibilidade com telas que usam apenas o primeiro setor."""
    return setores_do_usuario(usuario).first()
