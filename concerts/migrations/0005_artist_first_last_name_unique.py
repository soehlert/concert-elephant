# Generated by Django 4.2.4 on 2023-08-25 20:26

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0004_alter_artist_name"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="artist",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"), name="first_last_name_unique"
            ),
        ),
    ]