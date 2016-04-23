# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-03 11:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20160403_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='voteresult',
            name='vote_data',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='results.VoteData'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='citydata',
            name='citizen_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='citydata',
            name='town_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='voivodeshipdata',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='votedata',
            name='authorized_citizen_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='votedata',
            name='town',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='results.CityData'),
        ),
        migrations.AlterField(
            model_name='votedata',
            name='vote_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='votedata',
            name='vote_forms_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='voteresult',
            name='vote_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.RemoveField(
            model_name='voteresult',
            name='town',
        ),
        migrations.AlterUniqueTogether(
            name='voteresult',
            unique_together=set([('vote_data', 'candidate')]),
        ),
    ]