# Generated by Django 5.0.4 on 2024-05-06 01:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemini', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='tipoAcesso',
            field=models.CharField(default='aluno', editable=False, max_length=255),
        ),
        migrations.AlterField(
            model_name='aluno',
            name='email',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='coordenador',
            name='email',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='coordenador',
            name='tipoAcesso',
            field=models.CharField(default='coordenador', editable=False, max_length=255),
        ),
        migrations.CreateModel(
            name='Mensagem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('texto_mensagem', models.CharField(max_length=200)),
                ('data_hora', models.DateTimeField()),
                ('quem_enviou', models.CharField(max_length=255)),
                ('id_aluno', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gemini.aluno')),
                ('id_coordenador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gemini.coordenador')),
            ],
        ),
    ]