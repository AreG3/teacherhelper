from django.shortcuts import render
from kalendarz.models import Events


def index(request):
    return render(request, 'index.html')