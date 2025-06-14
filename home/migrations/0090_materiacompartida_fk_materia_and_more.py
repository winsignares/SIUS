# Generated by Django 5.1.3 on 2025-06-08 20:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0089_funcionessustantivas'),
    ]

    operations = [
        migrations.AddField(
            model_name='materiacompartida',
            name='fk_materia',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='home.materia', verbose_name='Materia con la que se comparte'),
        ),
        migrations.AlterField(
            model_name='materiacompartida',
            name='fk_periodo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.periodo', verbose_name='Periodo '),
        ),
        migrations.AlterField(
            model_name='materiacompartida',
            name='fk_programa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.programa', verbose_name='Programa con el que se comparte'),
        ),
    ]
