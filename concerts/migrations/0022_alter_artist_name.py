# Generated by Django 4.2.4 on 2023-10-23 05:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0021_remove_artist_artist_name_unique_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artist",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
