from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from django.views.static import serve
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_image_serve(request, path):
    try:
        return serve(request, path, settings.MEDIA_ROOT)
    except ObjectDoesNotExist:
        return HttpResponse("Sorry you don't have permission to access this file")