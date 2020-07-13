from django.urls import include, path
from rest_framework import routers as drf_routers

from vectors.viewsets import VectorViewSet, TagViewSet

# Automatic routes
router = drf_routers.DefaultRouter()
router.register(r'vectors', VectorViewSet, basename='vector')
router.register(r'tags', TagViewSet, basename='tag')

# Other urls
vector_urls = [
    path('', include(router.urls)),
]
