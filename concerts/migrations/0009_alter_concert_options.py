# Generated by Django 4.2.4 on 2023-08-26 15:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0008_alter_concert_artist_alter_concert_venue"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="concert",
            options={"ordering": ["-date"]},
        ),
    ]
