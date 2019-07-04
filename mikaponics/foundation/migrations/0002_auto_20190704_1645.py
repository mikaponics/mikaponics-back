# Generated by Django 2.2.1 on 2019-07-04 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='time_step',
            field=models.DurationField(choices=[('00:01:00', 'Every minute'), ('00:05:00', 'Every 5 minutes'), ('00:15:00', 'Every 15 minutes'), ('00:30:00', 'Every 30 minutes'), ('01:00:00', 'Every hour')], default='00:01:00', help_text='The time difference between the previous time series datum to the new time-series datum. This is the interval which will be used for all time-series data generated.', verbose_name='Time Step'),
        ),
    ]