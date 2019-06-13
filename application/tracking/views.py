from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
"""
def index(request):
    return HttpResponse("Login")
"""

def index(request):
    return HttpResponse("Container List")

def detail(request):
    return HttpResponse("Container Detail")

def create(request):
    return HttpResponse("Container Create")
