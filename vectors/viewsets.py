from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from taggit.models import Tag

from vectors.serializers import (
    FeaturedSerializer,
    TaggitSerializer,
    VectorSerializer,
)
from vectors.filters import VectorsFilter
from vectors.pagination import StandardResultsSetPagination
from vectors.models import Vector, Featured


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vector.objects.all()
    serializer_class = VectorSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = VectorsFilter
    ordering_fields= ['uploaded']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest = self.get_queryset().order_by('-uploaded')[0:12].all()
        serializer = self.get_serializer(latest, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = Featured.objects.order_by('order')[0:6].all()
        serializer = FeaturedSerializer(featured, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def total(self, request):
        total_vectors = Vector.objects.count()
        response = Response({'total_vectors': total_vectors}, status=200)
        return response
