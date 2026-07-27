from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Administracao", "0037_alter_audiocampainha_arquivo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuariosetor",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vinculos_setores",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuário",
            ),
        ),
        migrations.AddConstraint(
            model_name="usuariosetor",
            constraint=models.UniqueConstraint(
                fields=("usuario", "setor"),
                name="usuario_setor_unico",
            ),
        ),
    ]
