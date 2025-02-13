# Generated by Django 5.1.1 on 2024-10-03 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
