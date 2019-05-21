# Generated by Django 2.2.1 on 2019-05-20 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0003_auto_20190520_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertitem',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Unread'), (2, 'Read'), (3, 'Archived')], default=1, help_text='The state of alert.', verbose_name='State'),
        ),
    ]