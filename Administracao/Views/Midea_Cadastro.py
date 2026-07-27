import os

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

from Administracao.models import MidiaPainel, tb_Setores

from .login import active_user_required
from .permissoes import setores_permitidos, usuario_eh_admin


class MidiaCadastroForm(forms.ModelForm):
    setores = forms.ModelMultipleChoiceField(
        label="Setores de exibição",
        queryset=tb_Setores.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = MidiaPainel
        fields = (
            "tipo",
            "arquivo",
            "texto",
            "texto_tamanho_fonte",
            "texto_cor",
            "texto_alinhamento",
            "ordem",
            "ativo",
            "exibir_lateral",
            "exibir_popup",
            "setores",
        )
        widgets = {
            "tipo": forms.Select(attrs={"data-media-type": ""}),
            "arquivo": forms.FileInput(
                attrs={
                    "accept": ".png,.jpg,.jpeg,.webp,.mp4,.mov",
                    "data-media-upload": "",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        queryset_setores = kwargs.pop(
            "setores_permitidos",
            tb_Setores.objects.none(),
        )
        super().__init__(*args, **kwargs)
        self.fields["setores"].queryset = queryset_setores
        self.fields["tipo"].initial = "Imagem"
        self.fields["arquivo"].required = False
        self.fields["texto"].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        arquivo = cleaned_data.get("arquivo")
        texto = (cleaned_data.get("texto") or "").strip()

        if tipo == "Texto":
            cleaned_data["arquivo"] = None
            cleaned_data["texto"] = texto

            if not texto:
                self.add_error("texto", "Informe o texto que será exibido.")

            return cleaned_data

        cleaned_data["texto"] = None

        if not arquivo:
            self.add_error("arquivo", "Selecione o arquivo da mídia.")
            return cleaned_data

        extensao = os.path.splitext(arquivo.name)[1].lower()
        extensoes_imagem = {".png", ".jpg", ".jpeg", ".webp"}
        extensoes_video = {".mp4", ".mov"}

        if tipo == "Imagem" and extensao not in extensoes_imagem:
            self.add_error(
                "arquivo",
                "Para o tipo Imagem, selecione um arquivo PNG, JPG, JPEG ou WEBP.",
            )
        elif tipo == "Vídeo" and extensao not in extensoes_video:
            self.add_error(
                "arquivo",
                "Para o tipo Vídeo, selecione um arquivo MP4 ou MOV.",
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
def midia_cadastro(request):
    """Cadastra uma nova mídia visual ou textual."""
    queryset_setores = setores_permitidos(request.user)
    eh_admin = usuario_eh_admin(request.user)

    if not eh_admin and not queryset_setores.exists():
        messages.error(
            request,
            "Seu usuário não possui um setor vinculado. "
            "Vincule um setor antes de cadastrar uma mídia.",
        )
        return redirect("administracao:gestao_midias")

    if request.method == "POST":
        form = MidiaCadastroForm(
            request.POST,
            request.FILES,
            setores_permitidos=queryset_setores,
        )

        if form.is_valid():
            midia = form.save(commit=False)
            midia.save()
            midia.setores.set(form.cleaned_data["setores"])
            messages.success(request, "Mídia cadastrada com sucesso.")
            return redirect(
                "administracao:midia_detalhada",
                midia_id=midia.pk,
            )
    else:
        form = MidiaCadastroForm(setores_permitidos=queryset_setores)

    return render(
        request,
        "Administracao/Midea_Cadastro.html",
        {
            "form": form,
            "eh_admin": eh_admin,
        },
    )
