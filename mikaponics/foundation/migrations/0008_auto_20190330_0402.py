# Generated by Django 2.1.7 on 2019-03-30 04:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0007_auto_20190330_0254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='max_timestamp',
            field=models.DateTimeField(blank=True, help_text='The date and time that this maximum value occured on.', verbose_name='Timestamp of maximum value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='max_value',
            field=models.FloatField(blank=True, help_text='The largest possible value.', null=True, verbose_name='Maximum value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='mean_value',
            field=models.FloatField(blank=True, help_text='The mean value.', null=True, verbose_name='Mean value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='median_value',
            field=models.FloatField(blank=True, help_text='The median value.', null=True, verbose_name='Median value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='min_timestamp',
            field=models.DateTimeField(blank=True, help_text='The date and time that this minimum value occured on.', verbose_name='Timestamp of minimum value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='min_value',
            field=models.FloatField(blank=True, help_text='The lowest possible value.', null=True, verbose_name='Minimum value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='mode_value',
            field=models.FloatField(blank=True, help_text='The mode value.', null=True, verbose_name='Mode value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='mode_values',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='The mode values.', null=True, verbose_name='Mode values'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='range_value',
            field=models.FloatField(blank=True, help_text='The range value.', null=True, verbose_name='Range value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='slug',
            field=models.SlugField(help_text='The unique slug used for this instrument analysis when accessing details page.', max_length=127, unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='stedv_value',
            field=models.FloatField(blank=True, help_text='The standard deviation value.', null=True, verbose_name='Standard deviation value'),
        ),
        migrations.AlterField(
            model_name='instrumentanalysis',
            name='variance_value',
            field=models.FloatField(blank=True, help_text='The variance value.', null=True, verbose_name='Variance value'),
        ),
    ]
