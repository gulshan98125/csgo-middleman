# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-09 09:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgomiddleman', '0008_auto_20170708_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='expectedAmount',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='mobileNumber',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
