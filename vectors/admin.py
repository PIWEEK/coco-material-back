import base64

from django.contrib import admin
from django.utils.html import mark_safe

from vectors.models import Vector, Featured


admin.site.site_header = "CocoMaterial administration"
admin.site.site_title = "CocoMaterial site admin"
admin.site.enable_nav_sidebar = False


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main', {'fields': ('name', 'description', 'tags', 'uploaded')}),
        ('Vector', {'fields': (('svg', 'svg_image'),)}),
        ('Colored Vector', {'fields': (('stroke_color', 'fill_color'), ('colored_svg', 'colored_svg_image'))}),
    )
    list_display = ['description', 'name', 'svg_image_thumb', 'colored_svg_image_thumb', 'tags', 'stroke_color', 'fill_color']
    readonly_fields = ['svg_image', 'svg_image_thumb', 'colored_svg_image', 'colored_svg_image_thumb', 'uploaded']
    list_editable = ['name', 'stroke_color', 'fill_color', 'tags']
    list_filter = ['uploaded', 'tags']
    search_fields = ['name', 'description', 'tags__name']
    ordering = ["-uploaded"]
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def svg_image(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=250 height=250 />')

    @admin.display(description="image (b/w)")
    def svg_image_thumb(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=70 height=70 />')

    def colored_svg_image(self, obj):
        if not obj.colored_svg_content: return ""
        base64_svg = base64.b64encode(obj.colored_svg_content.encode('utf-8')).decode('utf-8')
        return mark_safe(f'<img src="data:image/svg+xml;base64,{base64_svg}" width=256 height=256 />')

    @admin.display(description="image (color)")
    def colored_svg_image_thumb(self, obj):
        if not obj.colored_svg_content: return ""
        base64_svg = base64.b64encode(obj.colored_svg_content.encode('utf-8')).decode('utf-8')
        return mark_safe(f'<img src="data:image/svg+xml;base64,{base64_svg}" width=70 height=70 />')

    class Media:
        css = {
            'all': ('coco_material/css/cocostyle.css',)
        }


@admin.register(Featured)
class FeaturedAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'order']
    list_editable = ['tag', 'order']
    save_on_top = True
