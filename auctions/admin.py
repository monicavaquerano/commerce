from django.contrib import admin
from .models import User, Listings, Comments, Bids, Category


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "password",
    )


class ListingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "image",
        "category",
        "start_bid",
        "user",
        "start_date",
        "end_date",
        "duration",
        "is_active",
    )
    filter_horizontal = ("category", "watchers")


admin.site.register(User, UserAdmin)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Category)
admin.site.register(Bids)
admin.site.register(Comments)


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
