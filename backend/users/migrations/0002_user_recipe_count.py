# Generated by Django 3.2.19 on 2023-06-05 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='recipe_count',
            field=models.IntegerField(default=0, verbose_name='recipe_count'),
        ),
    ]
