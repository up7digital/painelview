from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class AdministracaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Administracao'

    def ready(self):
        from .models import tb_Conexoes
        try:
            if not tb_Conexoes.objects.filter(nome_conexao="Conexão HU").exists():
                tb_Conexoes.objects.create(
                    nome_conexao="Conexão HU",
                    url_origem="https://novosga.huufma.br/",
                    ip_mercure="10.16.0.18",
                    porta_mercure=3000,
                    user_sga="adminsga",
                    pass_sga="@d1m1nSg@",
                    client_id="83cdc6721514aeb8b8616ea7de7a62e7",
                    client_secret="25c9403ec15d16ffa062eef2a3262eea098aebca7ca2f1119f84603497c1a69a77e6c38052118b44926f35e8215fbc5410c53b631353eb13c7f36baa4c5b9d53",
                )
        except (OperationalError, ProgrammingError):
            pass
