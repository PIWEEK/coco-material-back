from rest_framework import serializers
from taggit.models import Tag

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
        fields = ('id', 'url', 'name', 'tags', 'svg', 'colored_svg', 'stroke_color', 'fill_color')


class DetailedVectorSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer()

    class Meta:
        model = Vector
        fields = ('id', 'url', 'name', 'tags', 'svg', 'svg_content', 'colored_svg', 'colored_svg_content', 'stroke_color', 'fill_color')


class FeaturedSerializer(serializers.ModelSerializer):
    vectors = VectorSerializer(many=True)

    class Meta:
        model = Featured
        fields = '__all__'
