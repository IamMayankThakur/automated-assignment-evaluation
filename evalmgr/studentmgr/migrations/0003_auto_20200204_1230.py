# Generated by Django 3.0.3 on 2020-02-04 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studentmgr", "0002_auto_20200202_1837"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="email_member_2",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="team",
            name="email_member_3",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="team",
            name="email_member_4",
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
