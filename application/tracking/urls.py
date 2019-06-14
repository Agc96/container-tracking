from django.urls import path
from .views import container, location, user

urlpatterns = [
    # Inicio de sesión
    path('', user.index, name='index'),
    path('login/', user.login, name='login'),
    # Lista de contenedores
    path('container/', container.index, name='container-index'),
    path('container/import/', container.import_data, name='container-import'),
    path('container/export/', container.export_data, name='container-export'),
    # Nuevo contenedor
    path('container/create/', container.create, name='container-create'),
    path('container/save/', container.save, name='container-save'),
    # Detalles del contenedor
    path('container/<int:container_id>/', container.detail, name='container-detail'),
    # Opciones de usuario
    path('profile/', user.profile, name='profile'),
    path('logout/', user.logout, name='logout'),
    # Llamadas AJAX
    path('container/search/', container.search, name='container-search'),
    path('location/search/', location.search, name='location-search')
]
