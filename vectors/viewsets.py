from rest_framework import viewsets
from taggit.models import Tag

from vectors.serializers import VectorSerializer, TaggitSerializer
from vectors.models import Vector


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VectorSerializer

    def get_queryset(self):
        queryset = Vector.objects.all()
        tags = self.request.query_params.get('tags', None)
        tags = tags.split(',')
        if tags is not None:
            queryset = Vector.objects.filter(tags__name__in=tags).distinct()

        return queryset

