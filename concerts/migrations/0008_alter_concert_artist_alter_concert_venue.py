# Generated by Django 4.2.4 on 2023-08-26 03:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("concerts", "0007_alter_concert_venue"),
    ]

    operations = [
        migrations.AlterField(
            model_name="concert",
            name="artist",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="concerts", to="concerts.artist"
            ),
        ),
        migrations.AlterField(
            model_name="concert",
            name="venue",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="concerts", to="concerts.venue"
            ),
        ),
    ]
