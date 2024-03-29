from django.contrib import admin

from resources.models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [
        'slug', 'name', 'description',
    ]
    search_fields = ['name', 'slug', 'description']
