from django.contrib import admin
from .models import User, Listings, Comments, Bids, Category


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "first_name", "last_name"]


class ListingsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "description",
        "start_bid",
        "start_date",
        "user",
        "is_active",
    ]
    list_filter = [
        ("is_active", admin.BooleanFieldListFilter),
    ]

    filter_horizontal = ("watchers",)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "user", "comment", "datetime"]
    ordering = ["datetime", "listing"]
    list_filter = ["listing", "user"]


class BidsAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "amount", "user", "datetime"]
    ordering = ["listing"]
    list_filter = ["listing"]


admin.site.register(User, UserAdmin)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Category)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)


# from django.contrib import admin
# from .models import Flight, Airport, Passenger


# Register your models here.
# class FlightAdmin(admin.ModelAdmin):
# list_display = ("id", "origin", "destination", "duration")


# class PassengerAdmin(admin.ModelAdmin):
# filter_horizontal = ("flights",)


# admin.site.register(Airport)
# admin.site.register(Flight, FlightAdmin)
# admin.site.register(Passenger, PassengerAdmin)
