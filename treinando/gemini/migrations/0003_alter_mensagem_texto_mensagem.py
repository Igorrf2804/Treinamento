# Generated by Django 5.0.4 on 2024-05-14 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemini', '0002_aluno_tipoacesso_alter_aluno_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensagem',
            name='texto_mensagem',
            field=models.CharField(max_length=1000),
        ),
    ]