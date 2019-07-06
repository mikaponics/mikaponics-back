# Generated by Django 2.2.1 on 2019-07-05 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0006_auto_20190704_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productioncropinspection',
            name='at_duration',
            field=models.DurationField(blank=True, editable=False, help_text='The value that this crop inspection was saved during the duration of the productiion since start.', null=True, verbose_name='At duration'),
        ),
    ]
