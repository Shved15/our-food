from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='login')
def place_order(request):
    return render(request, 'orders/place-order.html')
