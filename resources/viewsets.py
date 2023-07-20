from rest_framework import viewsets
from resources.models import Resource
from resources.serializers import ResourceSerializer


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
