# Generated by Django 2.2.1 on 2019-05-14 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0003_auto_20190514_0109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productioninspection',
            name='review',
        ),
        migrations.AddField(
            model_name='productioninspection',
            name='did_pass',
            field=models.NullBooleanField(default=None, help_text='Indicates if the evaulation of the system resulted in a passing score.', verbose_name='Did pass?'),
        ),
    ]