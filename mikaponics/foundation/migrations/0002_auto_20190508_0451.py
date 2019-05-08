# Generated by Django 2.2.1 on 2019-05-08 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crop',
            name='type_of',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Plant'), (2, 'Fishstock'), (3, 'Animalstock'), (0, 'None')], help_text='The type of crop being grown in production.', verbose_name='Type of'),
        ),
    ]