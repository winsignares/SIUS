# Generated by Django 5.1.3 on 2025-05-24 01:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0082_programauser'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contrato',
            old_name='valor_contrato',
            new_name='valor_mensual_contrato',
        ),
        migrations.RemoveField(
            model_name='programa',
            name='auth_user',
        ),
    ]
