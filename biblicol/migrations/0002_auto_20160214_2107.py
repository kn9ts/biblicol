# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblicol', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bible',
            name='title',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
