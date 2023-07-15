from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramWordSimilarity
from django.db.models import Q
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
            .annotate(
                search_a=SearchVector("search_text", config="simple_unaccent"),
                search_b=SearchVector("search_text", config="english"),
            )
            .filter(Q(search_a=SearchQuery(tags, config="simple_unaccent")) | Q(search_b=SearchQuery(tags, config="english")))
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
