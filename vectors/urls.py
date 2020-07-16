from django.urls import include, path
from rest_framework import routers as drf_routers

from vectors.viewsets import VectorViewSet, TagViewSet
from vectors.views import Download

# Automatic routes
router = drf_routers.DefaultRouter()
router.register(r'vectors', VectorViewSet, basename='vector')
router.register(r'tags', TagViewSet, basename='tag')

# Other urls
vector_urls = [
    path('download/', Download.as_view(), name='me'),
    path('', include(router.urls)),
]
