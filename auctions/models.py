from django.contrib.auth.models import AbstractUser
# from djmoney.models.fields import MoneyField
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    CAR = 'CAR'
    CAT = 'CAT'
    DOG = 'DOG'
    ELECTRONICS = 'ELE'
    FASHION = 'FAS'
    HOME = 'HOM'
    HORSE = 'HOR'
    CATEGORY_CHOICES = [
        (CAR, 'Car'),
        (CAT, 'Cat'),
        (DOG, 'Dog'),
        (FASHION, 'Fashion'),
        (HOME, 'Home'),
        (HORSE, 'Horse')
        ]

    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, default=CAR)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500, blank=False)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='photos%Y%m%d')
    active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="listings", null=True)

    def __str__(self):
        return f"{self.title} {self.description} and is currently {'Active' if self.active else 'Inactive'}"

    # The current price of a listing is either the starting bid if the listing is new,
    # or if bids have been received, then the lasted bid will be the current price.
    # Note that the function returns a decimal rather than a Bid object as the
    # starting bid is a decimal.
    def get_max_bid(self):
        if Bid.objects.filter(listing_id=self.id).count():
            listing_bids = Bid.objects.filter(listing_id=self.id)
            return int(listing_bids.order_by('-bid')[0].bid)
        return self.starting_bid


class Comment(models.Model):
    comment = models.TextField(max_length=500, blank=False, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_bids")
    time = models.DateTimeField(auto_now_add=True)
    bid = models.DecimalField(max_digits=7, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="users_bids")


class WatchList(models.Model):
    listing = models.ManyToManyField(Listing, related_name="watched")
    user = models.ManyToManyField(User, related_name="watching")
