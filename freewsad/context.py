from django.shortcuts import get_object_or_404, redirect, render



def context(request):
    return {'site_name': 'My Awesome Site'}