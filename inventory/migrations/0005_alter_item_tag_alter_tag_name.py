# Generated by Django 4.1.3 on 2022-11-15 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_alter_tag_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="tag",
            field=models.ManyToManyField(null=True, to="inventory.tag"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
