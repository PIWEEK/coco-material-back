from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from taggit.models import Tag

from vectors.serializers import (
    DetailedVectorSerializer,
    FeaturedSerializer,
    TaggitSerializer,
    VectorSerializer,
)
from vectors.models import Vector, Featured

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TaggitSerializer


class VectorViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        tags = self.request.query_params.get('tags', None)
        queryset = Vector.objects.all()

        if tags is not None:
            tags = tags.split(',')
            for tag in tags:
                queryset = queryset.filter(tags__name__iexact=tag.strip())

            queryset = queryset.distinct()

        return queryset


    def get_serializer_class(self):
        if self.action == 'list':
            return VectorSerializer

        return DetailedVectorSerializer


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
