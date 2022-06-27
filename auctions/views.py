from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, BidForm, BidFormOwner, CommentForm

from .models import User, Listing, Bid, WatchList, Comment

app_name = 'auctions'


def index(request):
    if request.GET.get('category'):
        context = Listing.objects.filter(active=True, category=request.GET.get('category'))
    else:
        context = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {'active_listings': context})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        # Dev note - user1 with Password as the password.
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Reference: https://djangocentral.com/uploading-images-with-django/
@login_required
def listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        print(f'request.user.id is: {request.user.id}')
        print(f'request.user is: {request.user}')
        if form.is_valid():
            #user = User.objects.get(id=request.user.id)
            new_listing = form.save(commit=False)
            new_listing.user_id = request.user.id
            new_listing.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'auctions/listing.html', {'form': form, 'img_obj': img_obj})
    else:
        form = ListingForm()
    return render(request, 'auctions/listing.html', {'form': form})


@login_required
def bid(request, listing_id):
    listing_bid = Listing.objects.get(pk=listing_id)
    current_highest_bid = listing_bid.get_max_bid()
    bids = Bid.objects.filter(listing_id=listing_bid.id).order_by('-time')
    user = User.objects.get(pk=request.user.id)
    if WatchList.objects.filter(listing=listing_bid, user=user):
        watch_list_state = "Remove from"
    else:
        watch_list_state = "Add to"
    is_winner = False
    if bids and user.id != listing_bid.user_id and user.id == bids[0].bidder.id:
        is_winner = True
    comments = Comment.objects.filter(listing_id=listing_bid)
    print(f'comments is: {comments}')
    if request.method == 'POST':
        if user.id is not listing_bid.user_id:
            print(f'In bid view after POST - current_highest_bid is: {current_highest_bid}')
            form = BidForm(current_highest_bid, request.POST)
            if form.is_valid():
                print(f'request is: {request}')
                print(f'request.POST["bid"] is: {request.POST["bid"]}')
                new_bid = Bid(bid=request.POST["bid"], bidder=user, listing_id=listing_bid.id)
                new_bid.save()
                return HttpResponseRedirect(reverse("index"))
        # The owner of the listing cannot bid but can close the bidding process.
        else:
            form = BidFormOwner(request.POST)
            if form.is_valid():
                if 'active' in request.POST:
                    listing_bid.active = bool(request.POST['active'])
                else:
                    listing_bid.active = False
                listing_bid.save(update_fields=['active'])
                return HttpResponseRedirect(reverse('index'))
    else:
        print(f'in view.bid - just about to instantiate a BidForm - current_highest_bid is {current_highest_bid}')
        if user.id is not listing_bid.user_id:
            form = BidForm(current_highest_bid)
        else:
            form = BidFormOwner(initial={'active': listing_bid.active})
    # print(f"bids.order_by('-time')[0].bidder.id is {bids.order_by('-time')[0].bidder.id}")

    return render(request, 'auctions/bid.html', {'listing': listing_bid,
                                                 'bids': bids,
                                                 'user': user,
                                                 'form': form,
                                                 'comments': comments,
                                                 'watch_list_state': watch_list_state,
                                                 'is_winner': is_winner}
                  )


# A Watching list toggles between operations add to the watch list and the operation to remove remove
# the from watchlist.
# If the listing is in the users watchlist then remove it and redirect to the listing page and the
# embedded watchlist link should be updated to "Add to Watchlist".
# If the listing is is not in the users watchlist then add the Listing to the watchlist
# and redirect back to the listing page. The embedded link should updated to "Remove from watchlist"
@login_required
def watch(request, listing_id):
    print('entering the watch view')
    watch_listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    if WatchList.objects.filter(listing=watch_listing, user=user):
        print(f'deleting watched item {watch_listing.title}')
        WatchList.objects.get(listing=watch_listing, user=user).delete()
    else:
        new_item_to_watch = WatchList.objects.create()
        new_item_to_watch.listing.add(watch_listing)
        new_item_to_watch.user.add(user)
        # new_item_to_watch.save()
        key = int(new_item_to_watch.id)
        # new_entry = WatchList.objects.get(pk=key)
        # print(f'added item {watch_listing.id}: {watch_listing.title} to watchlist as pk {key} '
        #      f'user_id: {new_entry.user.filter(pk=user.id)[0]} and listing_id: {new_entry.listing.filter(pk=watch_listing.id)[0].id}')
        print(f'added item {watch_listing.id}: {watch_listing.title} to watchlist as pk {key} '
              f'user_id: {new_item_to_watch.user.filter(pk=user.id)[0]} and '
              f'listing_id: {new_item_to_watch.listing.filter(pk=watch_listing.id)[0].id}')
    return HttpResponseRedirect(reverse("bid", kwargs={'listing_id': watch_listing.id}))
    # return HttpResponseRedirect(reverse("index"))
    # return redirect(request.get_full_path())

@login_required
def watchlist(request):
    user = request.user
    watch_items = user.watching.all()
    listings = []
    print(f'watch_items is: {watch_items}')
    print(f'watch_items.count() is {watch_items.count()}')
    if watch_items.count() > 0:
        for watch_item in watch_items:
            print(f'In loop and watch_item is {watch_item}')
            print(f'watch_item.listing.all() is {watch_item.listing.all()}')
            if watch_item.listing.all()[0]:
                listings.append(watch_item.listing.all()[0])
    #print(f'listings is: {listings}')
    return render(request, 'auctions/watchlist.html', {'listings': listings})


def categories(request):
    return render(request, 'auctions/categories.html', {'categories': Listing.CATEGORY_CHOICES})

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(comment=request.POST["comment"],
                                  listing=Listing.objects.get(pk=listing_id))
            new_comment.save()
            return HttpResponseRedirect(reverse("bid", args=[listing_id]))
    form = CommentForm()
    return render(request, "auctions/comment.html", {"form": form,
                                                     "listing_id": listing_id})
