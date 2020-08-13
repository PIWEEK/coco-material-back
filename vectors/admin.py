from django.contrib import admin
from django.utils.html import mark_safe

from vectors.models import Vector


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main', {'fields': ('name', 'tags',)}),
        ('Vector', {'fields': ('svg', 'svg_image')}),
    )
    list_display = ['name', 'svg_image_thumb', 'tags']
    readonly_fields = ['svg_image', 'svg_image_thumb']
    list_editable = ['tags']
    list_filter = ['tags']
    search_fields = ['name', 'tags__name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def svg_image(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=250 height=250 />')

    def svg_image_thumb(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=70 height=70 />')

    class Media:
        css = {
            'all': ('coco_material/css/cocostyle.css',)
        }
