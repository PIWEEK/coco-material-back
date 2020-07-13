from rest_framework import serializers
from taggit.models import Tag

from vectors.models import Vector


class TaggitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagSerializer(serializers.ListField):
    tag = serializers.CharField()

    def to_representation(self, data):
        return ', '.join(data.values_list('name', flat=True))


class VectorSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer()

    class Meta:
        model = Vector
        fields = '__all__'

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        instance = super(VectorSerializer, self).create(validated_data)
        instance.tags.set(*tags)
        return instance

    def update(self, validated_data):
        instance = self.create(validated_data)
        return instance
