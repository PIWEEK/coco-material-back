from django.contrib import admin
from django.utils.html import mark_safe

from vectors.models import Vector


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main', {'fields': ('name', 'tags',)}),
        ('Vector', {'fields': ('svg', 'svg_image')}),
    )
    list_display = ['name', 'tag_list']
    readonly_fields = ['svg_image',]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def svg_image(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=200 height=200 />')
