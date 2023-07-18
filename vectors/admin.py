import base64
import pathlib
import tempfile
from os.path import basename
from zipfile import ZipFile

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ngettext

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from adminsortable2.admin import SortableAdminMixin

from vectors.models import Vector, Featured
from vectors.services import images as images_services


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Main', {
                'fields': (
                    'name', 'description', 'tags', 'search_text', 'uploaded'
                )
            }
        ),
        (
            'SVG', {
                'fields': (
                    ('svg', 'svg_image'),
                    ('colored_svg', 'colored_svg_image'),
                    ('stroke_color', 'fill_color'),
                ),
            }
        ),
        (
            'GIF', {
                'fields': (
                    ('gif', 'gif_image'),
                    ('colored_gif', 'colored_gif_image'),
                ),
            }
        ),
    )
    list_display = [
        'description',
        'svg_image_thumb', 'colored_svg_image_thumb',  'stroke_color', 'fill_color',
        'gif_image_thumb', 'colored_gif_image_thumb',
        'name', 'tags',
    ]
    readonly_fields = [
        'svg_image', 'svg_image_thumb', 'colored_svg_image', 'colored_svg_image_thumb',
        'gif_image', 'gif_image_thumb', 'colored_gif_image', 'colored_gif_image_thumb',
        'search_text', 'uploaded'
    ]
    list_editable = ['name', 'stroke_color', 'fill_color', 'tags']
    list_filter = [
        'uploaded',
        ('tags', RelatedDropdownFilter)
    ]
    search_fields = ['name', 'description', 'tags__name']
    ordering = ["-uploaded"]
    actions = [
        "recalculate_search_text",
        "get_stroke_svg_files"
    ]
    save_on_top = True

    class Media:
        css = {
            'all': ('coco_material/css/cocostyle.css',)
        }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    # Svg files
    def svg_image(self, obj):
        if not obj.svg: return ""
        return mark_safe(f'<img src="{obj.svg.url}" width=128 height=128 />')

    @admin.display(description="SVG (b/w)")
    def svg_image_thumb(self, obj):
        if not obj.svg: return ""
        return mark_safe(f'<img src="{obj.svg.url}" width=70 height=70 />')

    def colored_svg_image(self, obj):
        if not obj.colored_svg_content: return ""
        base64_svg = base64.b64encode(obj.colored_svg_content.encode('utf-8')).decode('utf-8')
        return mark_safe(f'<img src="data:image/svg+xml;base64,{base64_svg}" width=128 height=128 />')

    @admin.display(description="SVG (color)")
    def colored_svg_image_thumb(self, obj):
        if not obj.colored_svg_content: return ""
        base64_svg = base64.b64encode(obj.colored_svg_content.encode('utf-8')).decode('utf-8')
        return mark_safe(f'<img src="data:image/svg+xml;base64,{base64_svg}" width=70 height=70 />')

    # Gif files
    def gif_image(self, obj):
        if not obj.gif: return ""
        return mark_safe(f'<img src="{obj.gif.url}" width=128 height=128 />')

    @admin.display(description="GIF (b/w)")
    def gif_image_thumb(self, obj):
        if not obj.gif: return ""
        return mark_safe(f'<img src="{obj.gif.url}" width=70 height=70 />')

    def colored_gif_image(self, obj):
        if not obj.colored_gif: return ""
        return mark_safe(f'<img src="{obj.colored_gif.url}" width=128 height=128 />')

    @admin.display(description="GIF (color)")
    def colored_gif_image_thumb(self, obj):
        if not obj.colored_gif: return ""
        return mark_safe(f'<img src="{obj.colored_gif.url}" width=70 height=70 />')

    # Actions
    @admin.action(description='Recalculate search text')
    def recalculate_search_text(self, request, queryset):
        for obj in queryset:
            obj.recalculate_search_text()

        count = queryset.count()
        self.message_user(
            request,
            ngettext(
                '%d vector has its search text updated.',
                '%d vectors have their search text updated.',
                count,
            ) % count,
            messages.SUCCESS,
        )

    @admin.action(description='Get stroke svg files')
    def get_stroke_svg_files(self, request, queryset):
        with tempfile.TemporaryDirectory() as directory:
            # customize vectors' svg
            for vector in queryset.exclude(svg__isnull=True):
                images_services.customize_vector(
                    vector.svg, directory,
                    "000000", "none"
                )

            # Generate zip file
            zip_name = f"stroke_svg_files-{timezone.now().isoformat()}.zip"
            zip_file_name = f"{directory}/{zip_name}"
            svgs = pathlib.Path(directory).glob('*.svg')
            with ZipFile(zip_file_name, 'w') as zipfile:
                for svg in svgs:
                    zipfile.write(str(svg), basename(svg.name))

            # Return zip file
            with open(zip_file_name, 'rb') as f:
                zip_file = f.read()
                response = HttpResponse(zip_file, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
                return response


@admin.register(Featured)
class FeaturedAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = [ 'order', 'name', 'tag']
    list_display_links = ['name']
    list_editable = ['tag']
    sortable_by = []
    save_on_top = True
