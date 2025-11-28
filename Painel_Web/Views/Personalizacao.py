from django.http import HttpResponse
from django.template import loader


from Administracao.models import tb_Personalizacao

def personalizacao_css(request):
    # Recupera o registro único de personalização (ou cria se ainda não existir)
    tema, _ = tb_Personalizacao.objects.get_or_create(id=1)

    # Renderiza o template CSS
    template = loader.get_template("Painel_Web/Personalizacao.css")
    css = template.render({"tema": tema})

    return HttpResponse(css, content_type="text/css; charset=utf-8")
