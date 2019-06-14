from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('containers/', views.container_list, name='container-list'),
    path('containers/create/', views.container_create, name='container-create'),
    path('containers/import/', views.container_import, name='container-import'),
    path('containers/export/', views.container_export, name='container-export'),
    path('containers/save/', views.container_save, name='container-save'),
    path('containers/<int:container_id>/', views.container_detail, name='container-detail'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout')
]
