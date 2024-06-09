from django import forms
from .models import Coordenador, Aluno
from django.core.exceptions import ValidationError


class CoordenadorAdminForm(forms.ModelForm):
    nova_senha = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Coordenador
        exclude = ['senha']

    def save(self, commit=True):
        coordenador = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            coordenador.senha = nova_senha
        if commit:
            coordenador.save()
        return coordenador

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        if nova_senha == '':
            raise ValidationError("A senha não pode ser vazia.")
        return cleaned_data


class AlunoAdminForm(forms.ModelForm):
    nova_senha = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Aluno
        exclude = ['senha']

    def save(self, commit=True):
        aluno = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            aluno.senha = nova_senha
        if commit:
            aluno.save()
        return aluno

    def clean(self):
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha == '':
            raise ValidationError("A senha não pode ser vazia.")
        return nova_senha
