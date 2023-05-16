from django.shortcuts import render


def customer_profile(request):
    return render(request, 'customer/customer-profile.html')
