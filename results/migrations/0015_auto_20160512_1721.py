# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-12 17:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0014_accountdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('vote_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.VoteResult')),
            ],
        ),
        migrations.AlterField(
            model_name='accountdata',
            name='username',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
    ]
