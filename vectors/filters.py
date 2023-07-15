from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramWordSimilarity
from django_filters import rest_framework as filters
from vectors.models import Vector


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        tags = " ".join(value.split(','))

        # Full Text Search by tags
        return (
            qs
            .annotate(search=SearchVector("search_text", config="simple_unaccent"))
            .filter(search=SearchQuery(tags, config="simple_unaccent"))
            .distinct()
        )


class SimilarityFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        tags = " ".join(value.split(','))

        # Search by similarity
        return (
            qs
            .annotate(similarity=TrigramWordSimilarity(tags, 'search_text'))
            .filter(similarity__gt=0.35)
            .order_by('-similarity', 'uploaded')
        )


class VectorsFilter(filters.FilterSet):
    tags = TagsFilter(field_name="tags")
    similarity = SimilarityFilter(field_name="similarity")

    class Meta:
        model = Vector
        fields = ["tags", "similarity"]
