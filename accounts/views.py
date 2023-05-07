from django.http import HttpResponse
from django.shortcuts import render

from accounts.forms import UserForm


def register_user(request):
    form = UserForm
    context = {
        'form': form
    }
    return render(request, 'accounts/register-user.html', context)
