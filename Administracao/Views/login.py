from functools import wraps

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def active_user_required(view_func):
    """Permite acesso somente a usuários autenticados e ativos."""
    protected_view = user_passes_test(
        lambda user: user.is_authenticated and user.is_active,
        login_url="administracao:login",
    )(view_func)

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_active:
            auth_logout(request)
        return protected_view(request, *args, **kwargs)

    return wrapper


def login_view(request):
    """Autentica o usuário antes de encaminhá-lo às configurações."""
    redirect_to = request.POST.get("next") or request.GET.get("next")

    if not url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_to = reverse("administracao:configuracoes")

    if request.user.is_authenticated:
        if request.user.is_active:
            return redirect(redirect_to)
        auth_logout(request)

    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.is_active:
                auth_login(request, user)
                return redirect(redirect_to)
    else:
        form = AuthenticationForm(request=request)

    return render(
        request,
        "Administracao/login.html",
        {
            "form": form,
            "next": redirect_to,
        },
    )


@require_POST
def logout_view(request):
    """Encerra a sessão atual e retorna ao Painel Web."""
    auth_logout(request)
    return redirect("painel_home")
