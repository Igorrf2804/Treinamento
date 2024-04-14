from django.db import models

# Create your models here.
class Pergunta(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.CharField(max_length=100)
    pergunta = models.CharField(max_length=200)
    resposta = models.TextField(blank = True, editable=False)
    
    def __str__(self):
        return self.pergunta

class Usuario(models.Model):
    id = models.AutoField(primary_key = True)
    usuario = models.CharField(max_length = 50)
    senha = models.CharField(max_length = 30)
    email = models.CharField(max_length = 50, default = 'email')

class Script(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 100)
    descricao = models.CharField(max_length = 5000)

class Pessoa(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)

class Setor(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 150)
    pessoas = models.ForeignKey(Pessoa, on_delete = models.CASCADE, related_name = "pessoas")

class Indicador(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 100)
    descricao = models.CharField(max_length = 1000)

class Relatorio(models.Model):
    id = models.AutoField(primary_key = True)
    data_inicial = models.DateField()
    data_final = models.DateField()
    indicadores = models.ManyToManyField(Indicador)