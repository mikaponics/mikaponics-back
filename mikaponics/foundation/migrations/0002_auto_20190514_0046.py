# Generated by Django 2.2.1 on 2019-05-14 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productioninspection',
            name='review',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(5, 'Excellent'), (4, 'Bad'), (3, 'Average'), (2, 'Good'), (1, 'Excellent')], help_text='The review of the user for this crop at this time.', null=True, verbose_name='Review'),
        ),
    ]
