# Generated by Django 5.1.1 on 2024-10-27 16:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0002_place_stadiumphoto'),
        ('rows', '0004_remove_row_seats'),
    ]

    operations = [
        migrations.AddField(
            model_name='row',
            name='place',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='place.place'),
            preserve_default=False,
        ),
    ]
