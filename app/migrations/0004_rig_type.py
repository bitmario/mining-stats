# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180219_0146'),
    ]

    operations = [
        migrations.AddField(
            model_name='rig',
            name='type',
            field=models.CharField(choices=[('claymore', 'Claymore miner')], default='claymore', max_length=10, verbose_name='miner type'),
        ),
    ]
