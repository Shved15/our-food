from django.http import HttpResponse
from django.shortcuts import render


def register_user(request):
    return HttpResponse('This is user registration form')
