# Generated by Django 3.0.2 on 2020-02-29 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("facultymgr", "0011_delete_apitestmodel"),
    ]

    operations = [
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