from collections import namedtuple

from django.db import connection
from django.core.exceptions import EmptyResultSet, ObjectDoesNotExist

from rest_framework import serializers


Neighbor = namedtuple("Neighbor", "previous next")


def get_neighbors(obj, queryset=None):
    """Get the neighbors of a model instance.
    The neighbors are the objects that are at the left/right of `obj` in the results set.
    :param obj: The object you want to know its neighbors.
    :param queryset: Find the neighbors applying the constraints of this set (a Django queryset
        object).
    :return: Tuple `<left neighbor>, <right neighbor>`. Previows and right neighbors can be `None`.
    """

    try:
        base_sql, base_params = queryset.query.sql_with_params()
    except EmptyResultSet:
        return Neighbor(prev=None, next=None)

    query = """
        SELECT * FROM
                (SELECT "id",
                    ROW_NUMBER() OVER(),
                    LAG("id", 1) OVER() AS prev,
                    LEAD("id", 1) OVER() AS next
                FROM (%s) as ID_AND_ROW)
        AS SELECTED_ID_AND_ROW
        """ % (
        base_sql
    )
    query += " WHERE id=%s;"
    params = list(base_params) + [obj.id]

    cursor = connection.cursor()
    cursor.execute(query, params)
    sql_row_result = cursor.fetchone()

    if sql_row_result is None:
        return Neighbor(prev=None, next=None)

    prev_object_id = sql_row_result[2]
    next_object_id = sql_row_result[3]

    try:
        previous = queryset.get(id=prev_object_id)
    except ObjectDoesNotExist:
        previous = None
    try:
        next = queryset.get(id=next_object_id)
    except ObjectDoesNotExist:
        next = None

    return Neighbor(previous=previous, next=next)


class NeighborsSerializerMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["neighbors"] = serializers.SerializerMethodField("get_neighbors")

    def serialize_neighbor(self, neighbor):
        raise NotImplementedError

    def get_neighbors(self, obj):
        view, request = self.context.get("view", None), self.context.get("request", None)
        if view and request:
            queryset = view.filter_queryset(view.get_queryset())
            previous, next = get_neighbors(obj, queryset)
        else:
            previous = next = None

        return {
            "previous": self.serialize_neighbor(previous) if previous else None,
            "next": self.serialize_neighbor(next) if next else None,
        }
