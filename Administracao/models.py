import os
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError

class tb_Conexoes(models.Model):
    nome_conexao = models.CharField("Nome da conexão", max_length=100)
    url_origem = models.URLField("URL do SGA", max_length=255)
    ip_mercure = models.GenericIPAddressField("IP do Mercure", protocol="IPv4", help_text="Normalmente é o mesmo do servidor hospedado o SGA")
    porta_mercure = models.IntegerField("Porta do Mercure", max_length=5, default=3000)
    user_sga = models.CharField("User SGA", max_length=200)
    pass_sga = models.CharField("Senha SGA", max_length=200)
    client_id = models.CharField("Client ID SGA", max_length=200)
    client_secret = models.CharField("Client Secret SHA", max_length=200)

    class Meta:
        verbose_name = "Conexão"
        verbose_name_plural = "Conexões"
        db_table = "tb_conexoes"

    def __str__(self):
        return self.nome_conexao

# ------------------------------------------------------------------------------------------------------------

def validar_tamanho_arquivo(arquivo):
    limite_mb = 1
    if arquivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo excede o limite de {limite_mb}MB.")

def validar_extensao_arquivo(arquivo):
    extensoes_permitidas = [
        ".mp3", ".wav", ".ogg", ".aac", ".m4a"
    ]
    ext = os.path.splitext(arquivo.name)[1].lower()

    if ext not in extensoes_permitidas:
        raise ValidationError(
            f"Tipo de arquivo não permitido. Extensões aceitas: {', '.join(extensoes_permitidas)}"
        )

class AudioCampainha(models.Model):
    arquivo = models.FileField(
        upload_to="audios/",
        validators=[validar_tamanho_arquivo, validar_extensao_arquivo],
        verbose_name="Arquivo de áudio"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Áudio de Campainha"
        verbose_name_plural = "Áudios de Campainha"

    def __str__(self):
        # Retorna APENAS texto
        return os.path.basename(self.arquivo.name) if self.arquivo else "Sem arquivo"

# --------------------------------------------------------------------------------------------------------------
class tb_Painel(models.Model):
    STATUS_CHOICES = [
        ("Ativo", "Ativo"),
        ("Inativo", "Inativo"),
    ]
    nome = models.CharField("Nome do painel", max_length=100)
    conexao = models.ForeignKey(tb_Conexoes, on_delete=models.CASCADE, related_name="paineis", verbose_name="Conexão",)
    unidade_sga = models.IntegerField("Unidade (SGA)", null=True, blank=True)
    servicos_sga = JSONField("Serviços da unidade (SGA)", null=True, blank=True, help_text="Lista de IDs de serviços da unidade no SGA")
    audio_campainha = models.ForeignKey(AudioCampainha, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Campainha do painel", help_text="Áudio tocado quando uma senha é chamada")
    status = models.CharField("Status", max_length=8, choices=STATUS_CHOICES, default="Ativo",)


    class Meta:
        verbose_name = "Painel"
        verbose_name_plural = "Painéis"
        db_table = "tb_painel"

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"