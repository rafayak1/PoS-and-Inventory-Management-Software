# Generated by Django 4.1.3 on 2022-11-15 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, null=True)),
                ("price", models.IntegerField(null=True)),
                ("quantity", models.IntegerField(null=True)),
            ],
        ),
    ]
