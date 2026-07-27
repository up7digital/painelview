from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Administracao", "0026_alter_audiocampainha_arquivo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="midiapainel",
            name="texto",
            field=models.TextField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name="Texto para Exibição",
            ),
        ),
    ]
