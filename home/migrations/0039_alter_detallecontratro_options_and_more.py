# Generated by Django 5.1.3 on 2025-02-11 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0038_contrato_total_dias_laborados_detallecontratro'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detallecontratro',
            options={'verbose_name': 'Detalle de Contrato', 'verbose_name_plural': 'Detalles de Contrato'},
        ),
        migrations.AlterModelTable(
            name='detallecontratro',
            table='detalle_contrato',
        ),
    ]
