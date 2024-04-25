# Generated by Django 4.2.11 on 2024-04-24 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("transloadit", models.CharField(max_length=65536)),
                ("signature", models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256)),
                (
                    "uploaded_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("video", models.FileField(upload_to="")),
                ("thumbnail", models.FileField(upload_to="")),
                ("transcription", models.FileField(upload_to="")),
                ("text_in_video", models.FileField(upload_to="")),
                ("logo", models.FileField(upload_to="")),
                ("status", models.CharField(default="", max_length=16)),
                ("video_id", models.CharField(default="", max_length=32)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SearchResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("clip_count", models.IntegerField(default=0)),
                ("clips", models.CharField(default="", max_length=10240)),
                (
                    "video",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="core.video"
                    ),
                ),
            ],
        ),
    ]
