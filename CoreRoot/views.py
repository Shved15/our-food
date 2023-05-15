from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.shortcuts import render

from vendor.models import Vendor


def home(request):
    if 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        pnt = GEOSGeometry('POINT(%s %s)' % (lng, lat))

        vendors = Vendor.objects.filter(
            user_profile__location__distance_lte=(pnt, D(km=1000))).annotate(
            distance=Distance("user_profile__location", pnt)).order_by("distance")

        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)
