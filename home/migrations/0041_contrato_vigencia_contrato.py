# Generated by Django 5.1.3 on 2025-02-12 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0040_alter_detallecontratro_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='vigencia_contrato',
            field=models.BooleanField(default=False, verbose_name='Vigencia del Contrato'),
        ),
    ]
