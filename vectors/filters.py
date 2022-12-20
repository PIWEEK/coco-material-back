from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramWordSimilarity
from django_filters import rest_framework as filters
from vectors.models import Vector


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        tags = " ".join(value.split(','))

        # Full Text Search by tags
        qs_res = (
            qs
            .annotate(search=SearchVector("search_text", config="english"))
            .filter(search=SearchQuery(tags, config="english"))
            .distinct()
        )
        if qs_res.exists():
            return qs_res

        # Search by similarity
        qs_res = (
            qs
            .annotate(similarity=TrigramWordSimilarity(tags, 'search_text'))
            .filter(similarity__gt=0.35)
            .order_by('-similarity', 'uploaded')
        )

        return qs_res


class VectorsFilter(filters.FilterSet):
    tags = TagsFilter(field_name="tags")

    class Meta:
        model = Vector
        fields = ["tags"]
