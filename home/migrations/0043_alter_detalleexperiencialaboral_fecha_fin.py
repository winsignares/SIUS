# Generated by Django 5.1.3 on 2025-03-08 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0042_detalleacademico_codigo_convalidacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalleexperiencialaboral',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),
    ]
