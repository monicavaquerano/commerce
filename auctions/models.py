from datetime import timedelta, timezone
import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


class Category(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=300)
    start_bid = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    image = models.URLField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="listings", null=True
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    start_date = models.DateTimeField(auto_now_add=True)

    DURATIONS = [
        (3, "Three Days"),
        (7, "One Week"),
        (14, "Two Weeks"),
        (28, "Four Weeks"),
    ]

    duration = models.IntegerField(choices=DURATIONS, blank=False, default=28)

    is_active = models.BooleanField(default=True)

    def isFinish(self):
        if self.end_date < timezone.now() or self.is_active == False:
            return True
        else:
            return False

    def __str__(self):
        return f"Listing #{self.id}: {self.title}, by user {self.user}."


class Bids(models.Model):
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserBids")
    listing = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="listingBids"
    )
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-amount", "-datetime"]

    def __str__(self):
        return f"Bid #{self.id}: ${self.amount} on {self.listing} by {self.user}, at {self.datetime}"


class Comments(models.Model):
    comment = models.TextField(max_length=300)
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userComments"
    )
    listing = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="listingComments"
    )

    class Meta:
        ordering = ["-datetime"]

    def __str__(self):
        return f"Comment #{self.id}: {self.user} on {self.listing}: {self.comment}"


# from django.db import models


# Create your models here.
# class Airport(models.Model):
#     city = models.CharField(max_length=64)
#     code = models.CharField(max_length=3)

#     def __str__(self):
#         return f"{self.city} ({self.code})"


# class Flight(models.Model):
#     origin = models.ForeignKey(
#         Airport, on_delete=models.CASCADE, related_name="departures"
#     )
#     destination = models.ForeignKey(
#         Airport, on_delete=models.CASCADE, related_name="arrivals"
#     )
#     duration = models.IntegerField()

#     def __str__(self):
#         return f"{self.id}: {self.origin} to {self.destination}"


# class Passenger(models.Model):
#     first = models.CharField(max_length=64)
#     last = models.CharField(max_length=64)
#     flights = models.ManyToManyField(Flight, blank=True, related_name="passengers")

#     def __str__(self):
#         return f"{self.first} {self.last}"
