# Generated by Django 5.1.3 on 2024-12-13 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_detalleexperiencialaboral_anios_experiencia'),
    ]

    operations = [
        migrations.CreateModel(
            name='afp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'AFP',
                'verbose_name_plural': 'AFP',
                'db_table': 'afp',
            },
        ),
        migrations.CreateModel(
            name='arl',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'ARL',
                'verbose_name_plural': 'ARL',
                'db_table': 'arl',
            },
        ),
        migrations.CreateModel(
            name='cajas_compensacion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Caja de compensacion',
                'verbose_name_plural': 'Cajas de compensacion',
                'db_table': 'cajas_compensacion',
            },
        ),
        migrations.CreateModel(
            name='departamentos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Departamento',
                'verbose_name_plural': 'Departamentos',
                'db_table': 'departamentos',
            },
        ),
        migrations.CreateModel(
            name='eps',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'EPS',
                'verbose_name_plural': 'EPS',
                'db_table': 'eps',
            },
        ),
    ]