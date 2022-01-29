from rest_framework import serializers
from taggit.models import Tag

from vectors.commons.serializers.neighbors import NeighborsSerializerMixin
from vectors.models import Vector, Featured


class TaggitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagSerializer(serializers.ListField):
    tag = serializers.CharField()

    def to_representation(self, data):
        return ','.join(data.values_list('name', flat=True))


class VectorSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer()

    class Meta:
        model = Vector
        fields = ('id', 'url', 'name', 'tags', 'svg', 'svg_content', 'colored_svg', 'colored_svg_content', 'stroke_color', 'fill_color')


class NeighborVectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vector
        fields = ('id', 'url', 'name')
        depth = 0


class VectorWithNeighborsSerializer(NeighborsSerializerMixin, VectorSerializer):
    def serialize_neighbor(self, neighbor):
        return NeighborVectorSerializer(neighbor, context=self.context).data


class FeaturedSerializer(serializers.ModelSerializer):
    vectors = VectorSerializer(many=True)

    class Meta:
        model = Featured
        fields = '__all__'


class SuggestionSerializer(serializers.Serializer):
    suggestion = serializers.CharField(required=True, allow_blank=False, max_length=250)
