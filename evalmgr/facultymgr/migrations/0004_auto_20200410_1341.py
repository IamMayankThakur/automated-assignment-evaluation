# Generated by Django 3.0.4 on 2020-04-10 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("facultymgr", "0003_auto_20200406_2238"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evaluation",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(name="FacultyProfile",),
    ]
