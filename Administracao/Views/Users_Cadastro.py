from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from Administracao.models import UsuarioSetor, tb_Setores

from .login import active_user_required


User = get_user_model()


class UserCadastroForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        label="Perfil",
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    setores = forms.ModelMultipleChoiceField(
        label="Setores",
        queryset=tb_Setores.objects.order_by("nome_setor"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "groups",
            "setores",
            "is_active",
        )

    def save(self, commit=True):
        usuario = super().save(commit=commit)

        if commit:
            UsuarioSetor.objects.filter(usuario=usuario).delete()
            UsuarioSetor.objects.bulk_create(
                [
                    UsuarioSetor(usuario=usuario, setor=setor)
                    for setor in self.cleaned_data.get("setores", ())
                ]
            )

        return usuario


@active_user_required
@permission_required(
    (
        "auth.acesso_usuarios",
        "auth.cadastrar_usuarios",
    ),
    raise_exception=True,
)
@require_http_methods(["GET", "POST"])
def user_cadastro(request):
    """Cadastra um novo usuário."""
    if request.method == "POST":
        form = UserCadastroForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            messages.success(request, "Usuário cadastrado com sucesso.")
            return redirect("administracao:gestao_users")
    else:
        form = UserCadastroForm()

    return render(
        request,
        "Administracao/Users_Cadastro.html",
        {"form": form},
    )
