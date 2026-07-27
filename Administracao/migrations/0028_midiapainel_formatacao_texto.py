import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Administracao", "0027_alter_midiapainel_texto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="midiapainel",
            name="texto",
            field=models.TextField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Texto para Exibição",
            ),
        ),
        migrations.AddField(
            model_name="midiapainel",
            name="texto_tamanho_fonte",
            field=models.PositiveIntegerField(
                default=32,
                validators=[
                    django.core.validators.MinValueValidator(12),
                    django.core.validators.MaxValueValidator(120),
                ],
                verbose_name="Tamanho da fonte",
            ),
        ),
        migrations.AddField(
            model_name="midiapainel",
            name="texto_cor",
            field=models.CharField(
                default="#ffffff",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        regex="^#[0-9A-Fa-f]{6}$"
                    )
                ],
                verbose_name="Cor do texto",
            ),
        ),
        migrations.AddField(
            model_name="midiapainel",
            name="texto_alinhamento",
            field=models.CharField(
                choices=[
                    ("left", "Esquerda"),
                    ("center", "Centro"),
                    ("right", "Direita"),
                ],
                default="center",
                max_length=6,
                verbose_name="Alinhamento",
            ),
        ),
    ]
