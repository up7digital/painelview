def _texto_limpo(valor):
    if valor is None:
        return ""
    return " ".join(str(valor).strip().split())


def _senha_para_fala(senha):
    """Separa os caracteres para melhorar a pronúncia de senhas como A001."""
    return " ".join(
        caractere
        for caractere in _texto_limpo(senha)
        if not caractere.isspace()
    )


def preparar_vocalizacao(
    senha,
    local=None,
    numero_local=None,
    nome_cliente=None,
):
    """Monta os dados de vocalização enviados ao painel web."""
    nome_cliente = _texto_limpo(nome_cliente)
    senha_falada = _senha_para_fala(senha)
    local = _texto_limpo(local)
    numero_local = _texto_limpo(numero_local)
    destino = " ".join(parte for parte in (local, numero_local) if parte)

    partes = []
    if nome_cliente:
        partes.append(nome_cliente)
    if senha_falada:
        partes.append(f"Senha {senha_falada}")
    if destino:
        partes.append(destino)

    return {
        "texto": " ".join(partes),
        "idioma": "pt-BR",
    }
