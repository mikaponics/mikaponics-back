# Generated by Django 2.1.7 on 2019-03-18 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0002_product_payment_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='', help_text='A description of the product.', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='description',
            field=models.TextField(blank=True, default='', help_text='A description of the subscription.', null=True, verbose_name='Description'),
        ),
    ]