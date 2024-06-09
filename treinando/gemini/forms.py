from django import forms
from .models import Coordenador, Aluno


class CoordenadorAdminForm(forms.ModelForm):
    nova_senha = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Coordenador
        exclude = ['senha']

    def save(self, commit=True):
        coordenador = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            coordenador.set_senha(nova_senha)
        if commit:
            coordenador.save()
        return coordenador


class AlunoAdminForm(forms.ModelForm):
    nova_senha = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Aluno
        exclude = ['senha']

    def save(self, commit=True):
        aluno = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            aluno.set_senha(nova_senha)
        if commit:
            aluno.save()
        return aluno
