# Generated by Django 5.1.1 on 2024-10-28 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rows', '0009_alter_row_unique_together'),
        ('seats', '0004_seat_place_seat_sector'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='seat',
            unique_together={('row', 'name')},
        ),
    ]
