from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from taggit.models import Tag

from vectors.serializers import (
    FeaturedSerializer,
    TaggitSerializer,
    VectorSerializer,
    VectorWithNeighborsSerializer,
)
from vectors.filters import VectorsFilter
from vectors.pagination import StandardResultsSetPagination
from vectors.models import Vector, Featured


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vector.objects.all().exclude(svg__isnull=True)
    pagination_class = StandardResultsSetPagination
    filterset_class = VectorsFilter
    ordering_fields= ['uploaded']

    def get_serializer_class(self):
        if self.action == "retrieve":
            return VectorWithNeighborsSerializer
        return VectorSerializer

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest = self.get_queryset().order_by('-uploaded')[0:12].all()
        serializer = self.get_serializer(latest, many=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = Featured.objects.order_by('order').all()
        serializer = FeaturedSerializer(featured, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    @action(detail=False, methods=['get'])
    def total(self, request):
        total_vectors = self.queryset.count()
        return Response({'total_vectors': total_vectors}, status=200)
