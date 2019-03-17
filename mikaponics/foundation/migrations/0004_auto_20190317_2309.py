# Generated by Django 2.1.7 on 2019-03-17 23:09

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0003_user_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='onboarding_survey_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='The onboarding submitted survey data.', null=True, verbose_name='Survey data'),
        ),
        migrations.AddField(
            model_name='user',
            name='was_onboarded',
            field=models.BooleanField(blank=True, default=False, help_text='Was the user onboarded in our system?', verbose_name='Was Onboarded'),
        ),
    ]
