# Generated by Django 5.0.6 on 2024-06-16 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemini', '0003_conversa_data_hora'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversa',
            name='data_hora',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]