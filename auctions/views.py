from django.contrib.auth import authenticate, login, logout

# from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Bids, Comments, User, Category, Listings


def index(request):
    active_listings = Listings.objects.filter(is_active=True)
    categories = Category.objects.all()

    return render(
        request,
        "auctions/index.html",
        {
            "listings": active_listings,
            "categories": categories,
        },
    )


def listing(request, id):
    listingData = Listings.objects.get(pk=id)
    bidData = Bids.objects.filter(listing=id).first()
    bidTotal = len(Bids.objects.filter(listing=id))
    hasWatchers = request.user in listingData.watchers.all()
    comments = Comments.objects.filter(listing=listingData)
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listingData,
            "hasWatchers": hasWatchers,
            "comments": comments,
            "bids": bidData,
            "bidTotal": bidTotal,
        },
    )


def addComment(request, id):
    currentUser = request.user
    listingData = Listings.objects.get(pk=id)
    comment = request.POST["newComment"]

    newComment = Comments(
        comment=comment,
        user=currentUser,
        listing=listingData,
    )

    # Insert the object our database
    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id,)))


# REVISAR
def addBid(request, id):
    currentUser = request.user
    listingData = Listings.objects.get(pk=id)
    bidData = Bids.objects.filter(listing=id).first()
    bid = request.POST["newBid"]

    if float(bid) >= listingData.start_bid:
        try:
            currentBid = float(bidData.amount)
            bidTotal = len(Bids.objects.filter(listing=id))

            if float(bid) > currentBid:
                newBid = Bids(
                    amount=bid,
                    user=currentUser,
                    listing=listingData,
                )

                # Insert the object our database
                newBid.save()

                return render(
                    request,
                    "auctions/listing.html",
                    {
                        "listing": listingData,
                        "message": "Bid was updated successfully.",
                        "update": True,
                        "bids": newBid,
                        "bidTotal": bidTotal,
                    },
                )
            else:
                return render(
                    request,
                    "auctions/listing.html",
                    {
                        "listing": listingData,
                        "message": "Bid was not updated -new bid has to be higher than current bid.",
                        "update": False,
                        "bids": bidData,
                        "bidTotal": bidTotal,
                    },
                )

        except AttributeError:
            bidTotal = 1

            newBid = Bids(
                amount=bid,
                user=currentUser,
                listing=listingData,
            )

            # Insert the object our database
            newBid.save()

            return render(
                request,
                "auctions/listing.html",
                {
                    "listing": listingData,
                    "message": "Bid was updated successfully.",
                    "update": True,
                    "bids": newBid,
                    "bidTotal": bidTotal,
                },
            )

    else:
        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listingData,
                "message": "Bid was not updated -bid has to be equal or higher than starting price.",
                "update": False,
                "bids": bidData,
                "bidTotal": bidTotal,
            },
        )


def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.watchlist.all()
    return render(
        request,
        "auctions/watchlist.html",
        {
            "listings": listings,
        },
    )


def addWatchlist(request, id):
    listingData = Listings.objects.get(pk=id)
    currentUser = request.user
    listingData.watchers.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def removeWatchlist(request, id):
    listingData = Listings.objects.get(pk=id)
    currentUser = request.user
    listingData.watchers.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(name=categoryFromForm)
        active_listings = Listings.objects.filter(is_active=True, category=category)
        categories = Category.objects.all()

        return render(
            request,
            "auctions/index.html",
            {"listings": active_listings, "categories": categories},
        )


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_categories(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/categories.html", {"categories": categories})
    else:
        category = request.POST["category"]
        new_category = Category(name=category)
        new_category.save()
        return HttpResponseRedirect(
            reverse(
                "categories",
            )
        )


def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        durations = Listings.DURATIONS
        return render(
            request,
            "auctions/create.html",
            {"categories": categories, "durations": durations},
        )
    else:
        # Get data from form
        title = request.POST["title"]
        description = request.POST["description"]
        start_bid = request.POST["start_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        # start_date = timezone.now()
        end_date = request.POST["end_date"]
        duration = request.POST["duration"]

        # Who is the user?
        user = request.user

        # Get all content about the particualr category
        category_data = Category.objects.get(name=category)

        # Create a new listing object
        listing = Listings(
            title=title,
            description=description,
            start_bid=float(start_bid),
            image=image_url,
            category=category_data,
            user=user,
            end_date=end_date,
            duration=duration,
        )
        # Insert the object our database
        listing.save()

        # Redirect to index page
        return HttpResponseRedirect(reverse(index))


# @login_required
def edit_user(request):
    if request.method == "GET":
        return render(
            request,
            "auctions/user.html",
        )
