import datetime
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import Bids, Comments, User, Category, Listings


def index(request):
    # active_listings = Listings.objects.filter(is_active=True).order_by("-start_date")
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
    isOwner = request.user == listingData.user

    end_date = listingData.start_date + datetime.timedelta(days=listingData.duration)

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listingData,
            "hasWatchers": hasWatchers,
            "comments": comments,
            "bids": bidData,
            "bidTotal": bidTotal,
            "isOwner": isOwner,
            "end_date": end_date.date,
        },
    )


def closeAuction(request, id):
    listingData = Listings.objects.get(pk=id)
    listingData.is_active = False
    listingData.save()

    bidData = Bids.objects.filter(listing=id).first()
    bidTotal = len(Bids.objects.filter(listing=id))
    hasWatchers = request.user in listingData.watchers.all()
    comments = Comments.objects.filter(listing=listingData)
    isOwner = request.user == listingData.user

    # For time and duration
    end_date = listingData.start_date + datetime.timedelta(days=listingData.duration)

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listingData,
            "hasWatchers": hasWatchers,
            "comments": comments,
            "bids": bidData,
            "bidTotal": bidTotal,
            "isOwner": isOwner,
            "end_date": end_date.date,
            "update": True,
            "message": "Your auction is closed.",
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


def addBid(request, id):
    currentUser = request.user
    listingData = Listings.objects.get(pk=id)
    bidData = Bids.objects.filter(listing=id).first()
    bid = request.POST["newBid"].strip()

    # For time and duration
    end_date = listingData.start_date + datetime.timedelta(days=listingData.duration)

    if float(bid) >= listingData.start_bid and currentUser != listingData.user:
        try:
            currentBid = float(bidData.amount)
            bidTotal = len(Bids.objects.filter(listing=id)) + 1

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
                        "end_date": end_date.date,
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
                        "end_date": end_date.date,
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
                    "end_date": end_date.date,
                },
            )
    else:
        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listingData,
                "message": "Bid was not updated -bid has to be equal or higher than starting price. Auction owner cannot bid.",
                "update": False,
                "bids": bidData,
                "end_date": end_date.date,
            },
        )


def displayWatchlist(request):
    if request.method == "GET":
        return render(request, "auctions/watchlist.html")
    else:
        currentUser = request.user
        listings = currentUser.watchlist.filter(is_active=True)
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

        if categoryFromForm != "all":
            category = Category.objects.get(name=categoryFromForm)
            active_listings = Listings.objects.filter(is_active=True, category=category)
            categories = Category.objects.all()
            return render(
                request,
                "auctions/index.html",
                {"listings": active_listings, "categories": categories},
            )
        else:
            active_listings = Listings.objects.filter(is_active=True)
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
    categories = Category.objects.all()
    if request.method == "GET":
        return render(
            request,
            "auctions/categories.html",
            {"categories": categories},
        )
    else:
        category = request.POST["category"].strip().capitalize()
        try:
            existing_category = Category.objects.get(name=category)
            if existing_category:
                return render(
                    request,
                    "auctions/categories.html",
                    {
                        "message": "Category already exists.",
                        "categories": categories,
                    },
                )
        except:
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
        title = request.POST["title"].strip().capitalize()
        description = request.POST["description"].strip().capitalize()
        start_bid = request.POST["start_bid"].strip()
        image_url = request.POST["image_url"].strip()
        category = request.POST["category"]
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
            duration=duration,
        )
        # Insert the object our database
        listing.save()

        # Redirect to index page
        return HttpResponseRedirect(reverse(index))


# User
def edit_user(request):
    currentUser = request.user
    if request.method == "GET":
        try:
            # Listings data
            my_listings = Listings.objects.filter(user=currentUser)

            # Bid Data Raw SQL
            sql = f""" 
            SELECT * from auctions_bids 
            WHERE user_id = {currentUser.id} 
            GROUP BY listing_id 
            ORDER BY datetime DESC; """
            my_bids = Bids.objects.raw(sql)

            return render(
                request,
                "auctions/user.html",
                {
                    "my_listings": my_listings,
                    "bidListings": my_bids,
                },
            )
        except:
            return render(request, "auctions/user.html")
    else:
        username = request.POST["username"].strip()
        first_name = request.POST["first_name"].strip()
        last_name = request.POST["last_name"].strip()
        email = request.POST["email"].strip()

        User.objects.filter(id=currentUser.id).update(
            username=username, first_name=first_name, last_name=last_name, email=email
        )
        messages.success(request, "Your data has been updated!")
        return HttpResponseRedirect(reverse("user"))


# Arreglar los mensajes en las demas cosas y arreglar lo del tiempo
@login_required
def changePSW(request):
    if request.method == "POST":
        currentUser = request.user
        current_psw = request.POST["current_psw"]
        new_psw = request.POST["new_psw"]
        confirmation = request.POST["confirmation"]

        # Check if current password is valid
        checkPSW = currentUser.check_password(current_psw)

        if checkPSW:
            # Check if new password and confirmation match
            if new_psw != confirmation:
                messages.error(
                    request, "Your new password and confirmation don't match!"
                )
                return HttpResponseRedirect(reverse("user"))
            else:
                currentUser.set_password(new_psw)
                messages.success(request, "Your password has been changed!")
                return HttpResponseRedirect(reverse("user"))
        else:
            messages.error(request, "Password invalid!")
            return HttpResponseRedirect(reverse("user"))


def myActiveBids(request):
    if request.method == "POST":
        currentUser = request.user
        is_active = request.POST["is_active"]

        my_listings = Listings.objects.filter(user=currentUser)

        if is_active != "won":
            # Bid Data Raw SQL
            sql = f""" 
            SELECT * FROM auctions_bids 
            JOIN auctions_listings ON 
            auctions_listings.id = auctions_bids.listing_id 
            WHERE auctions_bids.user_id = {currentUser.id} 
            AND auctions_listings.is_active = {is_active} 
            GROUP BY listing_id ORDER BY datetime DESC; """
            my_active_bids = Bids.objects.raw(sql)

            return render(
                request,
                "auctions/user.html",
                {
                    "bidListings": my_active_bids,
                    "my_listings": my_listings,
                },
            )

        else:
            # Bid Data Raw SQL
            sql = f"""
            SELECT * FROM auctions_bids
            JOIN auctions_listings ON
            auctions_listings.id = auctions_bids.listing_id
            WHERE auctions_bids.user_id = {currentUser.id}
            AND auctions_listings.is_active = False
            GROUP BY listing_id ORDER BY datetime DESC, amount ASC; """
            won_bids = Bids.objects.raw(sql)
            return render(
                request,
                "auctions/user.html",
                {
                    "bidListings": won_bids,
                    "my_listings": my_listings,
                },
            )


def myActiveListings(request):
    if request.method == "POST":
        currentUser = request.user
        is_active = request.POST["is_active"]
        my_active_listings = Listings.objects.filter(
            is_active=is_active, user=currentUser
        )
        my_bids = Bids.objects.filter(user=currentUser)

    return render(
        request,
        "auctions/user.html",
        {
            "my_listings": my_active_listings,
            "bidListings": my_bids,
        },
    )
