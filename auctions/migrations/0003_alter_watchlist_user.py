# Generated by Django 4.0.4 on 2022-06-22 05:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_listing_starting_bid_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='user',
            field=models.ManyToManyField(related_name='watching', to=settings.AUTH_USER_MODEL),
        ),
    ]
