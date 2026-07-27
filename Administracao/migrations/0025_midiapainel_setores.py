from django.db import migrations, models


def copiar_setor_para_setores(apps, schema_editor):
    MidiaPainel = apps.get_model("Administracao", "MidiaPainel")

    for midia in MidiaPainel.objects.exclude(setor_id=None).iterator():
        midia.setores.add(midia.setor_id)


def restaurar_primeiro_setor(apps, schema_editor):
    MidiaPainel = apps.get_model("Administracao", "MidiaPainel")

    for midia in MidiaPainel.objects.iterator():
        primeiro_setor = midia.setores.order_by("pk").first()
        if primeiro_setor:
            midia.setor_id = primeiro_setor.pk
            midia.save(update_fields=["setor"])


class Migration(migrations.Migration):
    dependencies = [
        ("Administracao", "0024_tb_personalizacao_cor_texto_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="midiapainel",
            name="setores",
            field=models.ManyToManyField(
                blank=True,
                related_name="midias_visuais",
                to="Administracao.tb_setores",
                verbose_name="Setores de exibição",
            ),
        ),
        migrations.RunPython(
            copiar_setor_para_setores,
            restaurar_primeiro_setor,
        ),
        migrations.RemoveField(
            model_name="midiapainel",
            name="setor",
        ),
    ]
