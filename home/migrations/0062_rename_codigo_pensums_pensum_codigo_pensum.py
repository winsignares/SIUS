# Generated by Django 5.1.3 on 2025-05-15 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0061_remove_pensum_pensum_pensum_codigo_pensums'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pensum',
            old_name='codigo_pensums',
            new_name='codigo_pensum',
        ),
    ]
