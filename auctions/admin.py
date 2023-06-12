from django.contrib import admin
from .models import User, Listings, Comments, Bids, Category


# Register your models here.
class ListingsAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchers",)


admin.site.register(User)
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
