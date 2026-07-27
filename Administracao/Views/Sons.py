from pathlib import PurePosixPath

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from Administracao.models import AudioCampainha

from .login import active_user_required


class SomForm(forms.ModelForm):
    class Meta:
        model = AudioCampainha
        fields = ("arquivo",)
        widgets = {
            "arquivo": forms.FileInput(
                attrs={"accept": ".mp3,.wav,.ogg,.aac,.m4a,audio/*"}
            ),
        }


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_sons",
    ),
    raise_exception=True,
)
def gestao_sons(request):
    """Lista os arquivos de áudio disponíveis como campainha."""
    sons = list(AudioCampainha.objects.only("arquivo").order_by("arquivo"))

    for som in sons:
        som.nome_arquivo = PurePosixPath(som.arquivo.name).name

    return render(
        request,
        "Administracao/Sons.html",
        {"sons": sons},
    )


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_sons",
    ),
    raise_exception=True,
)
def som_cadastro(request):
    """Cadastra um novo som de campainha."""
    if request.method == "POST":
        form = SomForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Som cadastrado com sucesso.")
            return redirect("administracao:gestao_sons")
    else:
        form = SomForm()

    return render(
        request,
        "Administracao/Som_Cadastro.html",
        {"form": form},
    )


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_sons",
    ),
    raise_exception=True,
)
@require_POST
def som_excluir(request, som_id):
    """Exclui um som cadastrado."""
    som = get_object_or_404(AudioCampainha, pk=som_id)
    nome_arquivo = PurePosixPath(som.arquivo.name).name
    som.delete()

    messages.success(request, f'Som "{nome_arquivo}" excluído com sucesso.')
    return redirect("administracao:gestao_sons")
