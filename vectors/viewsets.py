from django.db.models import Q
from rest_framework import viewsets
from taggit.models import Tag

from vectors.serializers import DetailedVectorSerializer, VectorSerializer, TaggitSerializer
from vectors.models import Vector


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):

    def get_queryset(self):
        queryset = Vector.objects.all()
        tags = self.request.query_params.get('tags', None)
        if tags is not None:
            tags = tags.split(',')
            and_condition = Q()
            for tag in tags:
                and_condition.add(Q(tags__name=tag), Q.AND)

            queryset = Vector.objects.filter(and_condition).distinct()

        return queryset


    def get_serializer_class(self):
        if self.action == 'list':
            return VectorSerializer

        return DetailedVectorSerializer
