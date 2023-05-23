from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.shortcuts import render
from django.views import View

from vendor.models import Vendor


class HomeView(View):
    """View for main page representation."""

    template_name = 'home.html'

    @staticmethod
    def get_or_set_current_location(request):
        """Get or set the current location coordinates from the request."""
        if 'lat' in request.session:
            lat = request.session['lat']
            lng = request.session['lng']
            return lng, lat
        elif 'lat' in request.GET:
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            request.session['lat'] = lat
            request.session['lng'] = lng
            return lng, lat
        else:
            return None

    def get(self, request):
        """Handle GET requests to the home page."""
        if self.get_or_set_current_location(request) is not None:
            # Get the current location coordinates
            pnt = GEOSGeometry('POINT(%s %s)' % (self.get_or_set_current_location(request)))

            # Filter vendors within a certain distance from the current location
            vendors = Vendor.objects.filter(
                user_profile__location__distance_lte=(pnt, D(km=1000))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for vendor in vendors:
                # Calculate the distance in kilometers and round to one decimal place.
                vendor.kms = round(vendor.distance.km, 1)
        else:
            # If the current location is not available, retrieve a default list of vendors.
            vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

        context = {
            'vendors': vendors,
        }
        return render(request, self.template_name, context)
