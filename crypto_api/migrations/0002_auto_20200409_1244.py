# Generated by Django 3.0.4 on 2020-04-09 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trades',
            name='currency_in',
            field=models.CharField(choices=[('EUR', 'Euro'), ('USD', 'Dollar')], max_length=30),
        ),
    ]
