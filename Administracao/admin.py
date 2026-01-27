from django import forms
from django.db import models
from django.urls import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.contrib.admin.widgets import FilteredSelectMultiple

from .utils.sga_client import SGAClient

from .models import tb_Setores, tb_Conexoes, tb_Painel, AudioCampainha, MidiaPainel, ConfigPainel

from .forms import ConexoesForm

# Setores ===============================================================
@admin.register(tb_Setores)
class Setores(admin.ModelAdmin):
    list_display = ("nome_setor", "status")
    list_filter = ("nome_setor", "status")
    search_fields = ("nome_setor",)


# Mídeas Painel ===============================================================
@admin.register(MidiaPainel)
class MidiaPainelAdmin(admin.ModelAdmin):
    list_display = ("arquivo", "tipo", "ordem", "ativo", "setor")
    list_filter = ("tipo", "ativo", "exibir_popup", "setor")
    search_fields = ("arquivo",)
    ordering = ("ordem",)

    class Media:
        js = ("admin/js/painel_js.js",)

# Conexões ===================================================================
@admin.register(tb_Conexoes)
class ConexoesAdmin(admin.ModelAdmin):
    form = ConexoesForm
    list_display = ["nome_conexao"]
    search_fields = ["nome_conexao"]


class PainelForm(forms.ModelForm):
    # 1. SOBRESCREVE o campo no formulário
    servicos_sga = forms.MultipleChoiceField(
        label="Serviços da unidade (SGA)",
        required=False,
        # 2. DEFINE O WIDGET
        widget=FilteredSelectMultiple(
            "Serviços", # Título que será exibido no topo do widget
            is_stacked=False # Exibe em linha
        )
    )

    class Meta:
        model = tb_Painel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get("instance")
        conexao = None

        # Lógica para determinar a conexão (manter a lógica existente)
        # ... (seu código para carregar conexao)
        if instance and instance.pk:
            conexao = instance.conexao
        else:
            conexao_id = self.data.get("conexao")
            if conexao_id:
                try:
                    conexao = tb_Conexoes.objects.get(id=conexao_id)
                except tb_Conexoes.DoesNotExist:
                    conexao = None

        # Lógica para carregar Unidades e Serviços
        if conexao:
            try:
                sga = SGAClient(conexao)
                unidades = sga.listar_unidades()

                unidade_choices = [(u["id"], f'{u["id"]} - {u["nome"]}') for u in unidades]
                self.fields["unidade_sga"].widget = forms.Select(choices=unidade_choices)

                unidade_selecionada = (
                    self.data.get("unidade_sga")
                    or (instance.unidade_sga if instance else None)
                )

                if unidade_selecionada:
                    servicos = sga.listar_servicos(unidade_selecionada)

                    # 3. GARANTE QUE OS IDs SÃO STRINGS para o MultipleChoiceField
                    serv_choices = [
                        (str(s["servico"]["id"]), f'{s["sigla"]} - {s["servico"]["nome"]}')
                        for s in servicos
                    ]

                    # 4. PASSA AS OPÇÕES (CHOICES) E VALORES INICIAIS
                    self.fields["servicos_sga"].choices = serv_choices
                    
                    if instance and instance.servicos_sga:
                        # Carrega os valores salvos no JSONField
                        self.initial["servicos_sga"] = [str(id) for id in instance.servicos_sga]
                else:
                    self.fields["servicos_sga"].choices = []

            except Exception as e:
                print("Erro ao consultar SGA:", e)

# Gerenciamento das Campainha ===============================================================
@admin.register(AudioCampainha)
class AudioCampainhaAdmin(admin.ModelAdmin):

    readonly_fields = ("preview_audio",)

    def preview_audio(self, obj):
        """
        Exibe um player de áudio no Django Admin.
        """
        if obj.arquivo:
            return format_html(
                f"""
                <audio controls style="width: 300px; margin-top: 10px;">
                    <source src="{obj.arquivo.url}" type="audio/mpeg">
                    Seu navegador não suporta reprodução de áudio.
                </audio>
                """
            )
        return "Nenhum áudio enviado."

    preview_audio.short_description = "Prévia do áudio"

# Gerenciamento dos Painéis ===============================================================
@admin.register(tb_Painel)
class PainelAdmin(admin.ModelAdmin):
    form = PainelForm

    # 5. INCLUSÃO CRUCIAL: Adiciona o JS/CSS para o FilteredSelectMultiple funcionar
    class Media:
        # Pega a mídia do widget FilteredSelectMultiple
        js = ('/admin/js/core.js', '/admin/js/SelectBox.js', '/admin/js/SelectFilter2.js',)
        css = {
            'all': ('/admin/css/widgets.css',)
        }


# Configurações ===============================================================
@admin.register(ConfigPainel)
class ConfigPainelAdmin(admin.ModelAdmin):
    list_display = ("setor", "atualizado_em")
