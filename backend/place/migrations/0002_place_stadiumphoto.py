# Generated by Django 5.1.1 on 2024-10-17 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='stadiumPhoto',
            field=models.ImageField(blank=True, null=True, upload_to='stadium_photos/'),
        ),
    ]
