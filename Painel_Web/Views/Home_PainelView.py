from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from Administracao.models import tb_Painel, tb_Setores


class SelecionarPainelView(TemplateView):
    template_name = "Painel_Web/Home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["setores"] = tb_Setores.objects.filter(
            status="Ativo"
        ).order_by("nome_setor")
        return context


class SelecionarSetor(View):
    def get(self, request):
        setor_id = request.GET.get("setor")

        paineis = (
            tb_Painel.objects.filter(setor_id=setor_id, status="Ativo")
            .values("id", "nome")
            .order_by("nome")
        )

        return JsonResponse(list(paineis), safe=False)
