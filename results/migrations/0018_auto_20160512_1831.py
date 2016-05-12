# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-12 18:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0017_auto_20160512_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historydata',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='AccountData',
        ),
    ]
