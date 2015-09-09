# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150905_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='category_id',
        ),
        migrations.AddField(
            model_name='video',
            name='channel_id',
            field=models.CharField(default=0, max_length=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classifier',
            name='id',
            field=models.CharField(max_length=32, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='classifier',
            name='model_filename',
            field=models.CharField(max_length=48, null=True, blank=True),
        ),
    ]
