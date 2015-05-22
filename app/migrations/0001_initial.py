# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('author', models.TextField()),
                ('date', models.DateTimeField()),
                ('content', models.TextField()),
                ('tag', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('num_untrd_comments', models.IntegerField(default=0)),
                ('acc', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('stddev', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='video_id',
            field=models.ForeignKey(to='app.Video'),
        ),
    ]
