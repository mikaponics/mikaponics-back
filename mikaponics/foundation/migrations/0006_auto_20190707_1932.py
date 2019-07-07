# Generated by Django 2.2.1 on 2019-07-07 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0005_problemdatasheet'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncropinspection',
            name='abiotic_problems',
            field=models.ManyToManyField(blank=True, help_text='Stages of development this crop has in their lifespan.', related_name='production_crop_inspections_from_abiotic_problems', to='foundation.ProblemDataSheet'),
        ),
        migrations.AddField(
            model_name='productioncropinspection',
            name='disease_problems',
            field=models.ManyToManyField(blank=True, help_text='Stages of development this crop has in their lifespan.', related_name='production_crop_inspections_from_disease_problems', to='foundation.ProblemDataSheet'),
        ),
        migrations.AddField(
            model_name='productioncropinspection',
            name='pest_problems',
            field=models.ManyToManyField(blank=True, help_text='Stages of development this crop has in their lifespan.', related_name='production_crop_inspections_from_pest_problems', to='foundation.ProblemDataSheet'),
        ),
        migrations.AlterField(
            model_name='problemdatasheet',
            name='type_of',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Pest'), (2, 'Disease'), (3, 'Abiotic'), (4, 'None')], help_text='The type of production crop problem.', verbose_name='Type of'),
        ),
    ]