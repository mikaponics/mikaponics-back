# Generated by Django 2.2.1 on 2019-05-21 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0015_auto_20190521_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='production',
            name='evaluation_has_error',
            field=models.BooleanField(blank=True, default=False, editable=False, help_text='Indicates if there was an error with the evaluation or not.', verbose_name='Evaluation has Error?'),
        ),
    ]