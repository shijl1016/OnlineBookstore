# Generated by Django 2.2 on 2019-04-26 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ob', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obrecord',
            name='purchasing_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='purchaing date'),
        ),
    ]