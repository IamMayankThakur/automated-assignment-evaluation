# Generated by Django 3.0.3 on 2020-04-06 17:08

from django.db import migrations, models
import studentmgr.models


class Migration(migrations.Migration):

    dependencies = [
        ("facultymgr", "0002_auto_20200403_2349"),
    ]

    operations = [
        migrations.AddField(
            model_name="codeevalmodel",
            name="command",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="codeevalmodel",
            name="expected_output_file",
            field=models.FileField(null=True, upload_to="conf/expected_output/"),
        ),
        migrations.AlterField(
            model_name="codeevalmodel",
            name="docker_file",
            field=models.FileField(
                null=True,
                storage=studentmgr.models.OverwriteStorage(),
                upload_to="conf/dockerfile/",
            ),
        ),
    ]