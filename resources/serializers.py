from rest_framework import serializers

from resources.models import Resource


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
