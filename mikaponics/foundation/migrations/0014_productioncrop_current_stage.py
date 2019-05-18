# Generated by Django 2.2.1 on 2019-05-18 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0013_auto_20190518_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncrop',
            name='current_stage',
            field=models.PositiveSmallIntegerField(blank=True, default=1, help_text='The life cycle stage this crop is currently in. The only acceptable values are the values which are available in the `stages` data-sheet for the crop.', verbose_name='Currnet Life Cycle Stage'),
        ),
    ]
