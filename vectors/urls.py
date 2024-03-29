from django.urls import include, path
from rest_framework import routers as drf_routers

from vectors.viewsets import VectorViewSet, TagViewSet
from vectors.views import Download, Suggestion
from resources.viewsets import ResourceViewSet

# Automatic routes
router = drf_routers.DefaultRouter()
router.register(r'vectors', VectorViewSet, basename='vector')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'resources', ResourceViewSet, basename='resource')

# Other urls
vector_urls = [
    path('', include(router.urls)),
    path('download/', Download.as_view(), name='download'),
    path('suggestion/', Suggestion.as_view(), name='suggestion'),
]
