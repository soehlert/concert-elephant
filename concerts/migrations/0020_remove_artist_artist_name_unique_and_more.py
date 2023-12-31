# Generated by Django 4.2.4 on 2023-10-21 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0019_alter_venue_unique_together_artist_musicbrainz_id_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="artist",
            name="artist_name_unique",
        ),
        migrations.AddField(
            model_name="artist",
            name="processed_for_musicbrainz",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="artist",
            name="musicbrainz_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddConstraint(
            model_name="artist",
            constraint=models.UniqueConstraint(models.F("musicbrainz_id"), name="artist_name_unique"),
        ),
    ]
