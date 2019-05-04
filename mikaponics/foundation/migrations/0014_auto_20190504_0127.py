# Generated by Django 2.2.1 on 2019-05-04 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0013_auto_20190503_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='production',
            name='system',
        ),
        migrations.RemoveField(
            model_name='production',
            name='system_other',
        ),
        migrations.AddField(
            model_name='production',
            name='grow_system',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Wick System'), (2, 'Deep Water Culture System'), (3, 'Ebb & Flow System'), (4, 'Nutrient Film Technique System'), (5, 'Drip System'), (6, 'Aeroponic System'), (7, 'Vertical Tower System'), (8, 'Other (Please specify)')], default=1, help_text='The growth system being used for crop production.', verbose_name='Grow System'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='production',
            name='grow_system_other',
            field=models.CharField(blank=True, help_text='The description of the other growth system.', max_length=63, null=True, verbose_name='Grow System (Other)'),
        ),
    ]
