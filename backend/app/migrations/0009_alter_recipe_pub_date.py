# Generated by Django 3.2.19 on 2023-06-03 13:50

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20230603_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 3, 16, 50, 51, 406874), verbose_name='Дата публикации'),
        ),
    ]
