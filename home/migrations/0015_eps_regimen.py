# Generated by Django 5.1.3 on 2024-12-26 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_remove_eps_regimen'),
    ]

    operations = [
        migrations.AddField(
            model_name='eps',
            name='regimen',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]