from django.contrib import admin

from vectors.models import Vector


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    ...
