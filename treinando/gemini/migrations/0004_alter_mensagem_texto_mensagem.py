# Generated by Django 5.0.4 on 2024-05-14 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemini', '0003_alter_mensagem_texto_mensagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensagem',
            name='texto_mensagem',
            field=models.CharField(max_length=10000),
        ),
    ]