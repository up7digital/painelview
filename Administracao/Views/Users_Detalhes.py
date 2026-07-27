from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from Administracao.models import UsuarioSetor, tb_Setores

from .login import active_user_required


User = get_user_model()


class UserDetalhesForm(forms.ModelForm):
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

    class Meta:
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            vinculos = UsuarioSetor.objects.filter(
                usuario=self.instance
            ).values_list("setor_id", flat=True)
            self.fields["setores"].initial = list(vinculos)

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
@require_http_methods(["GET", "POST"])
def user_detalhes(request, user_id):
    """Exibe e atualiza os dados de um usuário."""
    permissoes = (
        ("auth.acesso_usuarios", "auth.editar_usuarios")
        if request.method == "POST"
        else ("auth.acesso_usuarios", "auth.visualizar_usuarios")
    )
    if not request.user.has_perms(permissoes):
        raise PermissionDenied

    usuario = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = UserDetalhesForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso.")
            return redirect(
                "administracao:user_detalhes",
                user_id=usuario.pk,
            )
    else:
        form = UserDetalhesForm(instance=usuario)

    return render(
        request,
        "Administracao/Users_Detalhes.html",
        {
            "usuario": usuario,
            "form": form,
        },
    )
