from rest_framework import viewsets
from taggit.models import Tag

from vectors.serializers import VectorSerializer, TaggitSerializer
from vectors.models import Vector


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vector.objects.all()
    serializer_class = VectorSerializer
