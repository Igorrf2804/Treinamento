# Generated by Django 5.0.4 on 2024-05-13 00:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemini', '0006_remove_setor_pessoas_setor_pessoas'),
    ]

    operations = [
        migrations.AddField(
            model_name='pergunta',
            name='indicador',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='indicador', to='gemini.indicador'),
        ),
    ]
