# Generated by Django 4.1.3 on 2022-11-15 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_alter_item_tag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(
                choices=[("Active", "Active"), ("Inactive", "Inactive")],
                max_length=100,
                null=True,
            ),
        ),
    ]
