from django.contrib import admin
from django.utils.html import mark_safe

from vectors.models import Vector, Featured


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main', {'fields': ('name', 'tags', 'uploaded')}),
        ('Vector', {'fields': (('svg', 'svg_image'),)}),
        ('Colored Vector', {'fields': (('stroke_color', 'fill_color'), ('colored_svg', 'colored_svg_image'))}),
    )
    list_display = ['name', 'svg_image_thumb', 'colored_svg_image_thumb', 'tags', 'stroke_color', 'fill_color', 'uploaded']
    readonly_fields = ['svg_image', 'svg_image_thumb', 'colored_svg_image', 'colored_svg_image_thumb', 'uploaded']
    list_editable = ['stroke_color', 'fill_color', 'tags']
    list_filter = ['uploaded', 'tags']
    search_fields = ['name', 'tags__name']
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def svg_image(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=250 height=250 />')

    def svg_image_thumb(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=70 height=70 />')

    def colored_svg_image(self, obj):
        return mark_safe(f'<img src="{obj.colored_svg.url}" width=250 height=250 />') if obj.colored_svg else ""

    def colored_svg_image_thumb(self, obj):
        return mark_safe(f'<img src="{obj.colored_svg.url}" width=70 height=70 />') if obj.colored_svg else ""

    class Media:
        css = {
            'all': ('coco_material/css/cocostyle.css',)
        }


@admin.register(Featured)
class FeaturedAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'order']
    list_editable = ['tag', 'order']
    save_on_top = True
