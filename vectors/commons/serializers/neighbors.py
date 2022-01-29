from collections import namedtuple

from django.db import connection

from rest_framework import serializers


Neighbor = namedtuple("Neighbor", "left right")


def get_neighbors(obj, results_set=None):
    """Get the neighbors of a model instance.
    The neighbors are the objects that are at the left/right of `obj` in the results set.
    :param obj: The object you want to know its neighbors.
    :param results_set: Find the neighbors applying the constraints of this set (a Django queryset
        object).
    :return: Tuple `<left neighbor>, <right neighbor>`. Previows and right neighbors can be `None`.
    """
    if results_set is None or results_set.count() == 0:
        results_set = type(obj).objects.get_queryset()
    compiler = results_set.query.get_compiler('default')
    base_sql, base_params = compiler.as_sql()
    query = """
        SELECT * FROM
            (SELECT "id" as id, ROW_NUMBER() OVER()
                FROM (%s) as ID_AND_ROW)
        AS SELECTED_ID_AND_ROW
        """ % (base_sql)
    query += " WHERE id=%s;"
    params = list(base_params) + [obj.id]
    cursor = connection.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    if row is None:
        return Neighbor(None, None)
    obj_position = row[1] - 1
    try:
        left = obj_position > 0 and results_set[obj_position - 1] or None
    except IndexError:
        left = None
    try:
        right = results_set[obj_position + 1]
    except IndexError:
        right = None
    return Neighbor(left, right)


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
            left, right = get_neighbors(obj, results_set=queryset)
        else:
            left = right = None

        return {
            "previous": self.serialize_neighbor(left) if left else None,
            "next": self.serialize_neighbor(right) if right else None,
        }
