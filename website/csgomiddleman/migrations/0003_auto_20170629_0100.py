# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-28 19:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csgomiddleman', '0002_auto_20170629_0017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trade',
            old_name='redirected_link',
            new_name='random_string',
        ),
    ]
