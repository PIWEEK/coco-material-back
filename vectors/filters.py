from django_filters import rest_framework as filters

from vectors.models import Vector


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            tags = value.split(',')
            for tag in tags:
                qs = qs.filter(tags__name__iexact=tag.strip())
            qs = qs.distinct()

        return qs


class VectorsFilter(filters.FilterSet):
    tags = TagsFilter(field_name="tags")

    class Meta:
        model = Vector
        fields = ["tags"]
