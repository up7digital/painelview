import os
from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
#----------------------------------------------------------------------------------


class tb_Setores(models.Model):
    STATUS_CHOICES =[
        ("Ativo", "Ativo"),
        ("Inativo", "Inativo"),
    ]

    nome_setor = models.CharField("Nome do setor", max_length=20, null=True)
    status = models.CharField("Status",choices=STATUS_CHOICES, default="Ativo")

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"

    def __str__(self):
        return self.nome_setor


class UsuarioSetor(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vinculos_setores",
        verbose_name="Usuário",
    )
    setor = models.ForeignKey(
        tb_Setores,
        on_delete=models.SET_NULL,
        related_name="usuarios_vinculados",
        verbose_name="Setor",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Setor do usuário"
        verbose_name_plural = "Setores dos usuários"

        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "setor"),
                name="usuario_setor_unico",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.setor or 'Sem setor'}"


class tb_Conexoes(models.Model):
    nome_conexao = models.CharField("Nome da conexão", max_length=100)
    url_origem = models.URLField("URL do SGA", max_length=255)
    ip_mercure = models.GenericIPAddressField("IP do Mercure", protocol="IPv4", help_text="Normalmente é o mesmo do servidor hospedado o SGA")
    porta_mercure = models.IntegerField("Porta do Mercure", default=3000)
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

# Campainhas ==========================================================================================================
def validar_tamanho_arquivo(arquivo):
    limite_mb = 3
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
        upload_to="audios/", validators=[validar_tamanho_arquivo, validar_extensao_arquivo], verbose_name="Arquivo de áudio"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Áudio de Campainha"
        verbose_name_plural = "Áudios de Campainha"

    def __str__(self):
        return f"{self.arquivo}"
    
# ----------------------------------------------------------------------------------------------------------------
class tb_Personalizacao(models.Model):
    convencional = models.CharField(
        max_length=7, default='#0250C4', validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$')],
        verbose_name='Cor da fonte Convencional'
    )
    prioridade = models.CharField(
        max_length=7, default="#FF0000", validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$')],
        verbose_name='Cor da fonte Prioridade'
    )

    cor_texto = models.CharField(max_length=7, default="#ffffff", validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$')], verbose_name="Cor da fonte do texto")
    tamanho_texto = models.IntegerField(verbose_name="Tamanho da fonte")


# UPLOAD MÍDEAS ======================================================================================================
# ------- VALIDADORES -------
def validar_tamanho_arquivo(arquivo):
    limite_mb = 8
    if arquivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo excede o limite de {limite_mb}MB.")

def validar_extensao_arquivo(arquivo):
    ext = os.path.splitext(arquivo.name)[1].lower()
    extensoes_permitidas = [
        ".png", ".jpg", ".jpeg", ".webp",  # imagens
        ".mp4", ".mov"                    # vídeos
    ]
    if ext not in extensoes_permitidas:
        raise ValidationError("Extensão inválida. Envie imagens (png/jpg/webp) ou vídeos (mp4/mov).")

# ------- MODEL -------
class MidiaPainel(models.Model):

    TIPOS = (
        ("Imagem", "Imagem"),
        ("Vídeo", "Vídeo"),
        ("Texto", "Texto"),
    )
    POPUP_CHOICES = (
        (0, "Sim"),
        (1, "Não"),
    )

    ALINHAMENTO_TEXTO_CHOICES = (
        ("left", "Esquerda"),
        ("center", "Centro"),
        ("right", "Direita"),
    )

    setores = models.ManyToManyField(
        tb_Setores,
        related_name="midias_visuais",
        verbose_name="Setores de exibição",
        blank=True,
    )
    tipo = models.CharField(max_length=10, choices=TIPOS)
    arquivo = models.FileField(
        upload_to="midias_painel/", blank=True, null=True, validators=[validar_tamanho_arquivo, validar_extensao_arquivo],
    )
    texto = models.TextField(max_length=100, blank=True, null=True, verbose_name="Texto para Exibição",)
    texto_tamanho_fonte = models.PositiveIntegerField(
        default=32,
        validators=[MinValueValidator(12), MaxValueValidator(120)],
        verbose_name="Tamanho da fonte",
    )
    texto_cor = models.CharField(
        max_length=7,
        default="#ffffff",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$")],
        verbose_name="Cor do texto",
    )
    texto_alinhamento = models.CharField(
        max_length=6,
        choices=ALINHAMENTO_TEXTO_CHOICES,
        default="center",
        verbose_name="Alinhamento",
    )
    ordem = models.PositiveIntegerField(default=0)
    exibir_lateral = models.IntegerField(choices=POPUP_CHOICES, default=0, verbose_name="Exibir no Painel Lateral")
    exibir_popup = models.IntegerField(choices=POPUP_CHOICES, default=1, verbose_name="Exibir no Pop-Up")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Mídia do Painel"
        verbose_name_plural = "Mídias do Painel"

    def clean(self):
        if self.tipo == "Texto" and not self.texto:
            raise ValidationError({"texto": "Informe o texto para mídias do tipo Texto."})

        if self.tipo != "Texto" and not self.arquivo:
            raise ValidationError({"arquivo": "Informe o arquivo para este tipo de mídia."})


    def __str__(self):
        if self.tipo == "Texto":
            return self.texto or f"Mídia {self.pk}"
        return self.arquivo.name if self.arquivo else f"Mídia {self.pk}"
    

# Painel--------------------------------------------------------------------------------------------------------------
class tb_Painel(models.Model):
    STATUS_CHOICES = [
        ("Ativo", "Ativo"),
        ("Inativo", "Inativo"),
    ]
    setor = models.ForeignKey(tb_Setores, on_delete=models.CASCADE, related_name="paineis_setor", verbose_name="Setor Origem", blank=True, null=True)
    nome = models.CharField("Nome do painel", max_length=100)
    conexao = models.ForeignKey(tb_Conexoes, on_delete=models.CASCADE, related_name="paineis", verbose_name="Conexão",)
    unidade_sga = models.IntegerField("Unidade (SGA)", null=True, blank=True)
    servicos_sga = JSONField("Serviços da unidade (SGA)", null=True, blank=True, help_text="Lista de IDs de serviços da unidade no SGA")
    audio_campainha = models.ForeignKey(
        AudioCampainha, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Campainha do painel", help_text="Áudio tocado quando uma senha é chamada"
    )
    voz_vocalizacao = models.CharField(
        "Voz da vocalização",
        max_length=150,
        blank=True,
        default="",
        help_text="Voz instalada no navegador. Deixe em automático para usar uma voz em português.",
    )
    velocidade_vocalizacao = models.DecimalField(
        "Velocidade da voz",
        max_digits=3,
        decimal_places=2,
        default=0.90,
        validators=[MinValueValidator(0.50), MaxValueValidator(2.00)],
        help_text="Valores entre 0,50 e 2,00. O padrão é 0,90.",
    )
    tom_vocalizacao = models.DecimalField(
        "Tom da voz",
        max_digits=3,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.50), MaxValueValidator(2.00)],
        help_text="Valores entre 0,50 e 2,00. O padrão é 1,00.",
    )
    status = models.CharField("Status", max_length=8, choices=STATUS_CHOICES, default="Ativo",)

    class Meta:
        verbose_name = "Painel"
        verbose_name_plural = "Painéis"
        db_table = "tb_painel"

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"

# Configurações do Painel =====================================================================================
class ConfigPainel(models.Model):
    setor = models.ForeignKey(tb_Setores, on_delete=models.CASCADE, related_name="paineis_config", verbose_name="Configuração Setor",)
    tempo_exibicao_imagem = models.PositiveIntegerField(default=8)
    tempo_popup = models.PositiveIntegerField(default=10)
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Tempo até exibição do Pop-Up")

    class Meta:
        verbose_name = "Configuração do Painel"
        verbose_name_plural = "Configuração dos Painéis"

    def __str__(self):
        return f"Configuração {self.id}"


