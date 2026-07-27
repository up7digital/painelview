from django.contrib import admin

from .models import ConfigPainel, MidiaPainel, tb_Setores

# Setores ===============================================================
@admin.register(tb_Setores)
class Setores(admin.ModelAdmin):
    list_display = ("nome_setor", "status")
    list_filter = ("nome_setor", "status")
    search_fields = ("nome_setor",)


# Mídeas Painel ===============================================================
@admin.register(MidiaPainel)
class MidiaPainelAdmin(admin.ModelAdmin):
    list_display = ("identificacao", "tipo", "ordem", "ativo", "setores_vinculados")
    list_filter = ("tipo", "ativo", "exibir_popup", "setores")
    search_fields = ("arquivo", "texto")
    ordering = ("ordem",)

    @admin.display(description="Mídia")
    def identificacao(self, obj):
        return obj.texto if obj.tipo == "Texto" else obj.arquivo.name

    @admin.display(description="Setores")
    def setores_vinculados(self, obj):
        return ", ".join(
            obj.setores.order_by("nome_setor").values_list(
                "nome_setor",
                flat=True,
            )
        )

    class Media:
        js = ("admin/js/painel_js.js",)

# Configurações ===============================================================
@admin.register(ConfigPainel)
class ConfigPainelAdmin(admin.ModelAdmin):
    list_display = ("setor", "atualizado_em")
