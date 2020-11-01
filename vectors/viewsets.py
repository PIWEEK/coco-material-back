from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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
        queryset = Vector.objects

        if tags is not None:
            tags = tags.split(',')
            for tag in tags:
                queryset = queryset.filter(tags__name=tag)

            queryset = queryset.distinct()

        return queryset


    def get_serializer_class(self):
        if self.action == 'list':
            return VectorSerializer

        return DetailedVectorSerializer


    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest = self.get_queryset().order_by('-uploaded')[0:10].all()
        serializer = self.get_serializer(latest, many=True)
        return Response(serializer.data)
