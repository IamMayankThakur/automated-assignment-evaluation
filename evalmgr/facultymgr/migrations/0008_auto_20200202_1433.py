# Generated by Django 3.0.2 on 2020-02-02 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facultymgr", "0007_auto_20200202_1244"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evaluation",
            name="access_code",
            field=models.CharField(max_length=256, null=True, unique=True),
        ),
    ]
