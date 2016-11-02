# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-06 16:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mapa', '0002_auto_20160306_1703'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reporte',
            options={'ordering': ['estado', '-fecha']},
        ),
        migrations.AddField(
            model_name='reporte',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 3, 6, 16, 11, 12, 548729, tzinfo=utc), verbose_name='Fecha'),
            preserve_default=False,
        ),
    ]