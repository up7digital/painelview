from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class AdministracaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Administracao'

    def ready(self):
        from .models import tb_Conexoes
        try:
            if not tb_Conexoes.objects.filter(nome_conexao="Conexão Principal").exists():
                tb_Conexoes.objects.create(
                    nome_conexao="Conexão Principal",
                    url_origem="https://seudns.seudominio.br/",
                    ip_mercure="IP do mércure",
                    porta_mercure=3000,
                    user_sga="Usuário do GLPI",
                    pass_sga="Senha do usuário GLPi",
                    client_id="Client ID do seu GLPI",
                    client_secret="Client Secret do seu GLPI",
                )
        except (OperationalError, ProgrammingError):
            pass
