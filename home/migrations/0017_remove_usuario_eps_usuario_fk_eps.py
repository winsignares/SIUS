# Generated by Django 5.1.3 on 2024-12-26 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_eps_nombre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='eps',
        ),
        migrations.AddField(
            model_name='usuario',
            name='fk_eps',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.eps'),
        ),
    ]