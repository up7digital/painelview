from django import forms
from .models import tb_Conexoes

class ConexoesForm(forms.ModelForm):
    class Meta:
        model = tb_Conexoes
        fields = "__all__"
        widgets = {
            "pass_sga": forms.PasswordInput(render_value=True),
            "client_secret": forms.PasswordInput(render_value=True),
        }
