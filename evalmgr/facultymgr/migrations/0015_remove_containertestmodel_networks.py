# Generated by Django 3.0.4 on 2020-03-11 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("facultymgr", "0014_auto_20200305_1940"),
    ]

    operations = [
        migrations.RemoveField(model_name="containertestmodel", name="networks",),
    ]
