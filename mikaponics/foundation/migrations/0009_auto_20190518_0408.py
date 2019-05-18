# Generated by Django 2.2.1 on 2019-05-18 04:08

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0008_auto_20190518_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncrop',
            name='evaluation_dict',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='The evaluation details for this particular score in the present date and time.', max_length=511, null=True, verbose_name='Evaluation Dictionary'),
        ),
        migrations.AddField(
            model_name='productioncrop',
            name='evaluation_score',
            field=models.FloatField(blank=True, default=0.0, help_text='The evaluation score of the current crop in the current present date and time.', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100)], verbose_name='Evaluation'),
        ),
    ]
