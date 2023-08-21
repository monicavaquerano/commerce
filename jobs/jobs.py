from django.conf import settings
import datetime
import requests
import json

# from django.db import IntegrityError

# from .models import Bids, Comments, User, Category, Listings
from auctions import models


def schedule_closing():
    listingData = models.Listings.objects.filter(is_active=True)

    for listing in listingData:
        start = listing.start_date.date()
        duration = listing.duration
        end_date = start + datetime.timedelta(days=duration)
        now = datetime.datetime.now().date()

        if end_date < now:
            # SEGUIR TRABAJANDO EN ESTO SI NO FUNCIONA
            # listing.objects.update(is_active=False)
            listingData.is_active = False
            listingData.save()

        else:
            print(f"Todavía no venzo! Venzo el {end_date}, y hoy es {now}")

    print("I'm working!")


# def closeAuction(request, id):
#     listingData = Listings.objects.get(pk=id)
#     listingData.is_active = False
#     listingData.save()

#     bidData = Bids.objects.filter(listing=id).first()
#     bidTotal = len(Bids.objects.filter(listing=id))
#     hasWatchers = request.user in listingData.watchers.all()
#     comments = Comments.objects.filter(listing=listingData)
#     isOwner = request.user == listingData.user

#     # For time and duration
#     end_date = listingData.start_date + datetime.timedelta(days=listingData.duration)

#     return render(
#         request,
#         "auctions/listing.html",
#         {
#             "listing": listingData,
#             "hasWatchers": hasWatchers,
#             "comments": comments,
#             "bids": bidData,
#             "bidTotal": bidTotal,
#             "isOwner": isOwner,
#             "end_date": end_date.date,
#             "update": True,
#             "message": "Your auction is closed.",
#         },
#     )
