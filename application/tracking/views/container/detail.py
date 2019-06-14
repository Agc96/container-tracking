from django.shortcuts import render

from ...models import Carrier, MockUser

def detail(request, container_id):
    """Detalles de un contenedor marítimo."""
    return render(request, 'tracking/container/detail.html', {
        'user': MockUser(),
        'container_id': container_id,
        'carriers': Carrier.objects.all()
    })
