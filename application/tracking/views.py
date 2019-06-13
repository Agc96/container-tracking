from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, 'tracking/login.html', {
        'logged': False
    })

def login(request):
    return HttpResponseRedirect(reverse('container-list'))

def container_list(request):
    return render(request, 'tracking/container/list.html', {
        'logged': True,
        'fullname': 'Anthony Gutiérrez',
        'role': 'Administrador'
    })

def container_detail(request, container_id):
    return render(request, 'tracking/container/detail.html', {
        'logged': True,
        'fullname': 'Anthony Gutiérrez',
        'role': 'Administrador',
        'container_id': container_id
    })

def container_create(request):
    return HttpResponse("Container Create")

def profile(request):
    return HttpResponse('TODO: Perfil')

def logout(request):
    return HttpResponse('TODO: Logout')
