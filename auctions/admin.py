from django.contrib import admin
from .models import Comment
from .models import Listing
from .models import User
from .models import Bid
from .models import WatchList


# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'active', 'image', 'get_user')

    def get_user(self, obj):
        return obj.user.username

    get_user.admin_order_field = 'username'
    get_user.short_description = 'user'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_listing_title', 'comment')

    def get_listing_title(self, obj):
        return obj.listing.title

    get_listing_title.admin_order_field = 'title'
    get_listing_title.short_description = 'Listing Title'


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


class BidAdmin(admin.ModelAdmin):
    list_display = ('get_listing_title', 'bid', 'get_bidder')

    def get_listing_title(self, obj):
        return obj.listing.title

    def get_bidder(self, obj):
        return obj.bidder.username

    get_listing_title.admin_order_field = 'title'
    get_listing_title.short_description = 'Listing Title'
    get_bidder.admin_order_field = 'username'
    get_bidder.short_description = 'bidder'

class WatchListAdmin(admin.ModelAdmin):
    list_display = ('get_listing_title', 'get_watcher')

    def __str__(self):
        return self.get_watcher() + ' ' + self.get_listing_title()

    def get_listing_title(self, obj):
        return obj.listing.title

    def get_watcher(self, obj):
        return obj.bidder.username

    get_listing_title.admin_order_field = 'title'
    get_listing_title.short_description = 'Listing Title'
    get_watcher.admin_order_field = 'username'
    get_watcher.short_description = 'watcher'


admin.site.register(Comment, CommentAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(WatchList)

