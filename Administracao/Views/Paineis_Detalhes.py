from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from Administracao.models import tb_Conexoes, tb_Painel
from Administracao.utils.sga_client import SGAClient

from .login import active_user_required


class PainelForm(forms.ModelForm):
    servicos_sga = forms.MultipleChoiceField(
        label="Serviços da unidade (SGA)",
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )
    voz_vocalizacao = forms.ChoiceField(
        label="Voz da vocalização",
        required=False,
        choices=(("", "Automática — voz em português"),),
        help_text=(
            "Voz instalada no navegador. Deixe em automático para usar "
            "uma voz em português."
        ),
    )

    class Meta:
        model = tb_Painel
        fields = (
            "setor",
            "nome",
            "conexao",
            "unidade_sga",
            "servicos_sga",
            "audio_campainha",
            "voz_vocalizacao",
            "velocidade_vocalizacao",
            "tom_vocalizacao",
            "status",
        )
        widgets = {
            "unidade_sga": forms.Select(),
            "voz_vocalizacao": forms.Select(),
            "velocidade_vocalizacao": forms.NumberInput(
                attrs={"min": "0.50", "max": "2.00", "step": "0.05"}
            ),
            "tom_vocalizacao": forms.NumberInput(
                attrs={"min": "0.50", "max": "2.00", "step": "0.05"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sga_error = None
        self.fields["unidade_sga"].widget.choices = [
            ("", "Selecione uma conexão primeiro")
        ]
        self.fields["servicos_sga"].choices = []
        voz_atual = (
            self.data.get("voz_vocalizacao")
            if self.is_bound
            else self.instance.voz_vocalizacao
        )
        escolhas_vozes = [
            ("", "Automática — voz em português")
        ]
        if voz_atual:
            escolhas_vozes.append(
                (voz_atual, voz_atual)
            )
        self.fields["voz_vocalizacao"].choices = escolhas_vozes
        self.fields["voz_vocalizacao"].widget.choices = escolhas_vozes

        conexao = self._obter_conexao()
        unidade_id = self.data.get("unidade_sga") if self.is_bound else None

        if not unidade_id and self.instance and self.instance.pk:
            unidade_id = self.instance.unidade_sga

        servicos_selecionados = self._servicos_selecionados()

        if conexao:
            try:
                sga = SGAClient(conexao)
                unidades = sga.listar_unidades()
                self.fields["unidade_sga"].widget.choices = [
                    ("", "Selecione uma unidade"),
                    *[
                        (str(unidade["id"]), f'{unidade["id"]} - {unidade["nome"]}')
                        for unidade in unidades
                    ],
                ]

                if unidade_id:
                    servicos = sga.listar_servicos(unidade_id)
                    self.fields["servicos_sga"].choices = [
                        (
                            str(servico["servico"]["id"]),
                            f'{servico["sigla"]} - {servico["servico"]["nome"]}',
                        )
                        for servico in servicos
                    ]
            except Exception:
                self.sga_error = (
                    "Não foi possível consultar unidades e serviços no Novo SGA. "
                    "Os valores atuais foram preservados."
                )

        self._preservar_opcoes_atuais(unidade_id, servicos_selecionados)

        if not self.is_bound:
            self.initial["servicos_sga"] = servicos_selecionados

    def _obter_conexao(self):
        conexao_id = self.data.get("conexao") if self.is_bound else None

        if not conexao_id and self.instance and self.instance.pk:
            conexao_id = self.instance.conexao_id

        if not conexao_id:
            return None

        try:
            return tb_Conexoes.objects.get(pk=conexao_id)
        except (tb_Conexoes.DoesNotExist, TypeError, ValueError):
            return None

    def _servicos_selecionados(self):
        if self.is_bound:
            return [str(item) for item in self.data.getlist("servicos_sga")]

        if self.instance and self.instance.pk and self.instance.servicos_sga:
            return [str(item) for item in self.instance.servicos_sga]

        return []

    def _preservar_opcoes_atuais(self, unidade_id, servicos_selecionados):
        if unidade_id:
            escolhas_unidades = list(self.fields["unidade_sga"].widget.choices)
            ids_unidades = {str(valor) for valor, _ in escolhas_unidades}

            if str(unidade_id) not in ids_unidades:
                escolhas_unidades.append(
                    (str(unidade_id), f"Unidade {unidade_id}")
                )
                self.fields["unidade_sga"].widget.choices = escolhas_unidades

        escolhas_servicos = list(self.fields["servicos_sga"].choices)
        ids_servicos = {str(valor) for valor, _ in escolhas_servicos}

        for servico_id in servicos_selecionados:
            if servico_id not in ids_servicos:
                escolhas_servicos.append(
                    (servico_id, f"Serviço {servico_id}")
                )

        self.fields["servicos_sga"].choices = escolhas_servicos

    def clean_servicos_sga(self):
        return [int(servico_id) for servico_id in self.cleaned_data["servicos_sga"]]


@active_user_required
@permission_required(
    "Administracao.gerenciar_paineis",
    raise_exception=True,
)
def painel_cadastro(request):
    """Cadastra um novo painel."""
    if request.method == "POST":
        form = PainelForm(request.POST)

        if form.is_valid():
            painel = form.save()
            messages.success(request, "Painel cadastrado com sucesso.")
            return redirect(
                "administracao:painel_detalhes",
                painel_id=painel.pk,
            )
    else:
        form = PainelForm()

    return render(
        request,
        "Administracao/Paineis_Detalhes.html",
        {
            "form": form,
            "modo_cadastro": True,
        },
    )


@active_user_required
@permission_required(
    "Administracao.gerenciar_paineis",
    raise_exception=True,
)
def painel_detalhes(request, painel_id):
    """Exibe e atualiza a ficha de um painel."""
    painel = get_object_or_404(tb_Painel, pk=painel_id)

    if request.method == "POST":
        form = PainelForm(request.POST, instance=painel)

        if form.is_valid():
            form.save()
            messages.success(request, "Painel atualizado com sucesso.")
            return redirect(
                "administracao:painel_detalhes",
                painel_id=painel.pk,
            )
    else:
        form = PainelForm(instance=painel)

    return render(
        request,
        "Administracao/Paineis_Detalhes.html",
        {
            "painel": painel,
            "form": form,
        },
    )
