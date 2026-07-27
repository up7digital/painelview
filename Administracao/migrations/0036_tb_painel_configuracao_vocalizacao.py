from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Administracao", "0035_alter_audiocampainha_arquivo"),
    ]

    operations = [
        migrations.AddField(
            model_name="tb_painel",
            name="voz_vocalizacao",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Voz instalada no navegador. Deixe em automático "
                    "para usar uma voz em português."
                ),
                max_length=150,
                verbose_name="Voz da vocalização",
            ),
        ),
        migrations.AddField(
            model_name="tb_painel",
            name="velocidade_vocalizacao",
            field=models.DecimalField(
                decimal_places=2,
                default=0.90,
                help_text="Valores entre 0,50 e 2,00. O padrão é 0,90.",
                max_digits=3,
                validators=[
                    MinValueValidator(0.50),
                    MaxValueValidator(2.00),
                ],
                verbose_name="Velocidade da voz",
            ),
        ),
        migrations.AddField(
            model_name="tb_painel",
            name="tom_vocalizacao",
            field=models.DecimalField(
                decimal_places=2,
                default=1.00,
                help_text="Valores entre 0,50 e 2,00. O padrão é 1,00.",
                max_digits=3,
                validators=[
                    MinValueValidator(0.50),
                    MaxValueValidator(2.00),
                ],
                verbose_name="Tom da voz",
            ),
        ),
    ]
