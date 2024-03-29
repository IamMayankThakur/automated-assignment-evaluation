# Generated by Django 3.0.4 on 2020-04-15 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import studentmgr.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Evaluation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("conf_file", models.FileField(upload_to="conf/eval/")),
                ("name", models.CharField(max_length=128)),
                ("type", models.IntegerField(null=True)),
                (
                    "access_code",
                    models.CharField(max_length=256, null=True, unique=True),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("begins_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("ends_on", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ScaleTestModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scale_min", models.IntegerField()),
                ("scale_max", models.IntegerField()),
                ("metric", models.TextField()),
                ("window", models.TextField()),
                ("up_threshold", models.TextField()),
                ("down_threshold", models.TextField()),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
            ],
            options={"managed": True,},
        ),
        migrations.CreateModel(
            name="ContainerTestModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("container_name", models.TextField()),
                ("container_image", models.TextField()),
                ("ports_exposed", models.TextField(blank=True)),
                ("connected_to_networks", models.TextField(blank=True)),
                ("env_variables", models.TextField(blank=True)),
                ("volumes", models.TextField(blank=True)),
                ("commands", models.TextField(blank=True)),
                ("num_cpus", models.IntegerField(blank=True)),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
            ],
            options={"managed": True,},
        ),
        migrations.CreateModel(
            name="CodeEvalTestModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("test_name", models.TextField(default="hidden")),
                ("sanity", models.BooleanField(default=False)),
                ("length_input1", models.TextField()),
                ("length_input2", models.TextField(blank=True)),
                ("expected_output", models.TextField(blank=True)),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
            ],
            options={"managed": True,},
        ),
        migrations.CreateModel(
            name="CodeEvalModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "docker_file",
                    models.FileField(
                        null=True,
                        storage=studentmgr.models.OverwriteStorage(),
                        upload_to="conf/dockerfile/",
                    ),
                ),
                ("main_file", models.FileField(null=True, upload_to="conf/mainfile/")),
                (
                    "expected_output_file",
                    models.FileField(null=True, upload_to="conf/expected_output/"),
                ),
                ("command", models.TextField(null=True)),
                (
                    "evaluation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
            ],
            options={"managed": True,},
        ),
        migrations.CreateModel(
            name="ApiTestModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("test_name", models.TextField(default="hidden")),
                ("sanity", models.BooleanField(default=False)),
                ("api_endpoint", models.TextField()),
                ("api_method", models.CharField(max_length=16, null=True)),
                ("api_message_body", models.TextField(blank=True)),
                ("expected_status_code", models.IntegerField()),
                ("expected_response_body", models.TextField(blank=True)),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
            ],
            options={"managed": True,},
        ),
    ]
