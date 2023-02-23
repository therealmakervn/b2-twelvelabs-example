# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-01 16:18
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import cattube.storage_backends


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('assembly_id', models.CharField(max_length=256, unique=True)),
                ('transcoded', models.URLField()),
                ('thumbnail', models.URLField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
