# Generated by Django 5.1.1 on 2024-10-03 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_ticketcategory_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketcategory',
            name='name',
        ),
    ]
