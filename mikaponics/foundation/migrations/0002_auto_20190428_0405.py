# Generated by Django 2.1.7 on 2019-04-28 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='store',
        ),
        migrations.RemoveField(
            model_name='user',
            name='subscription_plan',
        ),
        migrations.DeleteModel(
            name='SubscriptionPlan',
        ),
    ]
