# Generated by Django 3.2.12 on 2022-04-19 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20220416_1053'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(fields=('name', 'start_datetime', 'end_datetime'), name='name_start_datetime_end_datetime_unique'),
        ),
    ]
