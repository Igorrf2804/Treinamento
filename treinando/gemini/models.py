from django.db import models

# Create your models here.

class Indicador(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 100)
    descricao = models.CharField(max_length = 1000)

    def __str__(self):
        return self.nome

class Pergunta(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.CharField(max_length=100)
    pergunta = models.TextField(max_length=10000)
    resposta = models.TextField(blank = True)
    indicador = models.ForeignKey(Indicador, related_name='indicador', blank=True, on_delete= models.SET_NULL, null=True)
    def __str__(self):
        return str(self.indicador) + ' ' + self.pergunta

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

    def __str__(self):
        return self.nome
    

class Setor(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length = 150)
    pessoas = models.ManyToManyField(Pessoa, related_name = "pessoas")
    

class Relatorio(models.Model):
    id = models.AutoField(primary_key = True)
    data_inicial = models.DateField()
    data_final = models.DateField()
    indicadores = models.ManyToManyField(Indicador)