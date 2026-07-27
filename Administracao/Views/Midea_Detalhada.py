import os
from pathlib import PurePosixPath

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from Administracao.models import MidiaPainel, tb_Setores

from .login import active_user_required
from .permissoes import setores_permitidos, usuario_eh_admin


class MidiaDetalhesForm(forms.ModelForm):
    setores = forms.ModelMultipleChoiceField(
        label="Setores de exibição",
        queryset=tb_Setores.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = MidiaPainel
        fields = (
            "ordem",
            "ativo",
            "arquivo",
            "texto",
            "texto_tamanho_fonte",
            "texto_cor",
            "texto_alinhamento",
            "exibir_lateral",
            "exibir_popup",
            "setores",
        )
        widgets = {
            "arquivo": forms.FileInput(
                attrs={"accept": ".png,.jpg,.jpeg,.webp,.mp4,.mov"}
            ),
        }

    def __init__(self, *args, **kwargs):
        queryset_setores = kwargs.pop(
            "setores_permitidos",
            tb_Setores.objects.none(),
        )
        super().__init__(*args, **kwargs)
        self.fields["setores"].queryset = queryset_setores
        self.fields["setores"].initial = self.instance.setores.filter(
            pk__in=queryset_setores.values("pk"),
        )
        self.tipo_original = self.instance.tipo

        if self.tipo_original == "Texto":
            self.fields.pop("arquivo")
        else:
            self.fields["arquivo"].required = False
            self.fields.pop("texto")
            self.fields.pop("texto_tamanho_fonte")
            self.fields.pop("texto_cor")
            self.fields.pop("texto_alinhamento")

    def clean(self):
        cleaned_data = super().clean()

        if self.tipo_original == "Texto":
            self.instance.tipo = "Texto"
            return cleaned_data

        arquivo = cleaned_data.get("arquivo") or self.instance.arquivo
        extensao = os.path.splitext(arquivo.name)[1].lower() if arquivo else ""
        extensoes_imagem = {".png", ".jpg", ".jpeg", ".webp"}
        extensoes_video = {".mp4", ".mov"}

        if extensao in extensoes_imagem:
            self.instance.tipo = "Imagem"
        elif extensao in extensoes_video:
            self.instance.tipo = "Vídeo"
        else:
            self.add_error(
                "arquivo",
                "Selecione um arquivo de imagem (PNG, JPG, JPEG ou WEBP) "
                "ou vídeo (MP4 ou MOV).",
            )

        return cleaned_data


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_mideas",
    ),
    raise_exception=True,
)
def midia_detalhada(request, midia_id):
    """Exibe e atualiza uma mídia visual ou textual."""
    queryset_setores = setores_permitidos(request.user)
    eh_admin = usuario_eh_admin(request.user)
    midias_do_setor = (
        MidiaPainel.objects.all()
        if eh_admin
        else MidiaPainel.objects.filter(
            setores__in=queryset_setores,
        ).distinct()
    )
    midia = get_object_or_404(
        midias_do_setor,
        pk=midia_id,
    )
    tipo_midia = midia.tipo
    nome_midia = (
        PurePosixPath(midia.arquivo.name).name
        if midia.arquivo
        else midia.texto
    )
    arquivo_url = midia.arquivo.url if midia.arquivo else None

    if request.method == "POST":
        if request.POST.get("acao") == "excluir":
            arquivo_nome = midia.arquivo.name if midia.arquivo else ""
            arquivo_storage = (
                midia.arquivo.storage
                if midia.arquivo
                else None
            )
            midia.delete()

            if arquivo_nome and arquivo_storage:
                arquivo_storage.delete(arquivo_nome)

            messages.success(request, "Mídia excluída com sucesso.")
            return redirect("administracao:gestao_midias")

        form = MidiaDetalhesForm(
            request.POST,
            request.FILES,
            instance=midia,
            setores_permitidos=queryset_setores,
        )

        if form.is_valid():
            midia = form.save(commit=False)
            midia.save()
            midia.setores.remove(*queryset_setores)
            midia.setores.add(*form.cleaned_data["setores"])
            messages.success(request, "Mídia atualizada com sucesso.")
            return redirect(
                "administracao:midia_detalhada",
                midia_id=midia.pk,
            )
    else:
        form = MidiaDetalhesForm(
            instance=midia,
            setores_permitidos=queryset_setores,
        )

    return render(
        request,
        "Administracao/Midea_Detalhada.html",
        {
            "midia": midia,
            "nome_midia": nome_midia,
            "tipo_midia": tipo_midia,
            "arquivo_url": arquivo_url,
            "form": form,
            "eh_admin": eh_admin,
        },
    )
