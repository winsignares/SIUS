# Generated by Django 5.1.3 on 2024-12-26 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_sedes_usuario_sede_donde_labora'),
    ]

    operations = [
        migrations.AddField(
            model_name='eps',
            name='codigo_eps',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
