# Generated by Django 2.2.1 on 2019-05-12 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0006_auto_20190512_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='production',
            name='failure_reason_at_finish',
        ),
        migrations.AddField(
            model_name='production',
            name='failure_reason',
            field=models.TextField(blank=True, help_text='The reason why this crop production was overall considered a failure by the user.', null=True, verbose_name='Failure Reason'),
        ),
    ]
