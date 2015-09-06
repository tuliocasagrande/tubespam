# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_video_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classifier',
            fields=[
                ('id', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('model_filename', models.CharField(max_length=20, null=True, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='video',
            name='acc',
        ),
        migrations.RemoveField(
            model_name='video',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='video',
            name='num_untrd_comments',
        ),
        migrations.RemoveField(
            model_name='video',
            name='stddev',
        ),
        migrations.AddField(
            model_name='video',
            name='category_id',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
