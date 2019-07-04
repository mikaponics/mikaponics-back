# Generated by Django 2.2.1 on 2019-07-04 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0005_auto_20190704_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='type_of',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Humidity'), (2, 'Air Temperature'), (3, 'Water Temperature'), (4, 'Total Volatile Organic Compound'), (5, 'Carbon Dioxide'), (6, 'Air Pressure'), (7, 'Altitude'), (8, 'Water Level'), (9, 'Power Usage'), (10, 'pH'), (11, 'Electrical Conductivity'), (12, 'Oxidation-Reduction Potential'), (13, 'Camera'), (14, 'Heat Vision'), (15, 'UV Light'), (16, 'Triad Spectroscopy'), (17, 'Illuminance'), (18, 'Soil Moisture'), (19, 'Soil Temperature')], help_text='The type of instrument this is.', verbose_name='type of'),
        ),
    ]
