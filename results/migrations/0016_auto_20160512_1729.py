# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-12 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0015_auto_20160512_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='historydata',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='results.AccountData'),
        ),
        migrations.AlterField(
            model_name='historydata',
            name='vote_result',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='results.VoteResult'),
        ),
    ]