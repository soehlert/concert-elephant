# Generated by Django 4.2.4 on 2023-10-21 06:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0018_venue_state"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="venue",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="artist",
            name="musicbrainz_id",
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
        migrations.AddConstraint(
            model_name="venue",
            constraint=models.UniqueConstraint(fields=("name", "city", "state"), name="unique_venue"),
        ),
    ]
