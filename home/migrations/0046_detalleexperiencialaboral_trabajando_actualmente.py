# Generated by Django 5.1.3 on 2025-03-08 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0045_remove_detalleexperiencialaboral_trabajando_actualmente'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleexperiencialaboral',
            name='trabajando_actualmente',
            field=models.BooleanField(default=False),
        ),
    ]
