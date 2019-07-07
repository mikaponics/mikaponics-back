# Generated by Django 2.2.1 on 2019-07-07 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncrop',
            name='average_measure_unit',
            field=models.CharField(blank=True, help_text='A unit of measurement used for the averages measurements.', max_length=15, null=True, verbose_name='Average Measure Unit of measurement'),
        ),
    ]