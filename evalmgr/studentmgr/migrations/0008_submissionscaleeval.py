# Generated by Django 3.0.4 on 2020-04-07 20:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import studentmgr.models


class Migration(migrations.Migration):

    dependencies = [
        ("facultymgr", "0016_remove_scaletestmodel_manager_ip"),
        ("studentmgr", "0007_submission_faculty_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubmissionScaleEval",
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
                ("username", models.CharField(blank=True, max_length=128)),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("marks", models.FloatField(default=-1)),
                ("message", models.TextField()),
                ("manager_ip", models.URLField()),
                (
                    "private_key_file",
                    models.FileField(
                        blank=True,
                        storage=studentmgr.models.OverwriteStorage(),
                        upload_to="key",
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facultymgr.Evaluation",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studentmgr.Team",
                    ),
                ),
            ],
        ),
    ]