# Generated by Django 5.1.1 on 2024-10-03 16:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
        ('orders', '0001_initial'),
        ('tickets', '0003_ticketcategory_delete_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ticket_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.ticketcategory'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.user'),
        ),
    ]
