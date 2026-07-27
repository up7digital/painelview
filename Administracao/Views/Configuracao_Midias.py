from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet, modelformset_factory
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from Administracao.models import ConfigPainel

from .login import active_user_required
from .permissoes import (
    setores_do_usuario,
    setores_permitidos,
    usuario_eh_admin,
)


OPCOES_TEMPO = (5, 8, 10, 15, 20, 30, 45, 60, 90, 120)


class ConfigPainelForm(forms.ModelForm):
    class Meta:
        model = ConfigPainel
        fields = ("tempo_exibicao_imagem", "tempo_popup")
        widgets = {
            "tempo_exibicao_imagem": forms.Select(),
            "tempo_popup": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nome_campo in ("tempo_exibicao_imagem", "tempo_popup"):
            valores = set(OPCOES_TEMPO)
            valor_atual = getattr(self.instance, nome_campo, None)

            if valor_atual is not None:
                valores.add(valor_atual)

            self.fields[nome_campo].widget.choices = [
                (valor, f"{valor} segundos")
                for valor in sorted(valores)
            ]


class ConfigPainelBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        ids_permitidos = set(
            self.get_queryset().values_list("pk", flat=True)
        )

        for form in self.forms:
            configuracao = form.cleaned_data.get("id")
            if (
                configuracao is not None
                and configuracao.pk not in ids_permitidos
            ):
                raise ValidationError(
                    "Uma configuração informada não pertence aos setores permitidos."
                )


ConfigPainelFormSet = modelformset_factory(
    ConfigPainel,
    form=ConfigPainelForm,
    formset=ConfigPainelBaseFormSet,
    extra=0,
)


def configuracoes_permitidas(usuario):
    """Limita as configurações ao setor do usuário, exceto para Admin."""
    eh_admin = usuario_eh_admin(usuario)
    queryset = ConfigPainel.objects.select_related("setor").order_by(
        "setor__nome_setor",
        "id",
    )

    if eh_admin:
        return queryset, True

    queryset_setores = setores_permitidos(usuario)
    if not queryset_setores.exists():
        return queryset.none(), False

    return queryset.filter(setor__in=queryset_setores), False


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_mideas",
    ),
    raise_exception=True,
)
@require_http_methods(["GET", "POST"])
def configuracao_midias(request):
    """Lista e atualiza as configurações de mídia permitidas ao usuário."""
    queryset, eh_admin = configuracoes_permitidas(request.user)
    formset = ConfigPainelFormSet(
        request.POST or None,
        queryset=queryset,
    )

    if request.method == "POST" and formset.is_valid():
        formset.save()
        messages.success(
            request,
            "Configurações das mídias atualizadas com sucesso.",
        )
        return redirect("administracao:configuracao_midias")

    return render(
        request,
        "Administracao/Configuracao_Midias.html",
        {
            "formset": formset,
            "eh_admin": eh_admin,
            "setores_usuario": setores_do_usuario(request.user),
        },
    )
