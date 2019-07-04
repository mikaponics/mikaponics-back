# Generated by Django 2.2.1 on 2019-07-03 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0004_product_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='short_description',
            field=models.CharField(help_text='The short description of this product.', max_length=127, verbose_name='Short Description'),
        ),
    ]