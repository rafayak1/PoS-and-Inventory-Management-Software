# Generated by Django 4.1.3 on 2022-11-29 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0009_order_complete"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
