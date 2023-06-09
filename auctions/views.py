from django.contrib.auth import authenticate, login, logout

# from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import User, Category, Listings


def index(request):
    active_listings = Listings.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": active_listings})


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
        return render(request, "auctions/listing.html", {"categories": categories})
    else:
        # Get data from form
        title = request.POST["title"]
        description = request.POST["description"]
        start_bid = request.POST["start_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        # start_date = timezone.now()

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
        )
        # Insert the object our database
        listing.save()
        # Redirect to index page
        return HttpResponseRedirect(
            reverse(
                "auctions:index",
            )
        )


# @login_required
def edit_user(request):
    if request.method == "GET":
        return render(
            request,
            "auctions/user.html",
        )

    # if request.method == "POST":
    #     username = request.POST["username"]
    #     fname = request.POST["fname"]
    #     lname = request.POST["lname"]
    #     email = request.POST["email"]

    # password = request.POST["password"]
    # confirmation = request.POST["confirmation"]

    # if password != confirmation:
    #     return render(
    #         request, "auctions/user.html", {"message": "Passwords must match."}
    #     )

    # Attempt to create new user
    # try:
    #     user = User.objects.get(username)
    #     user.save()
    # except IntegrityError:
    #     return render(
    #         request,
    #         "auctions/user.html",
    #         {"message": "Username not valid."},
    #     )
