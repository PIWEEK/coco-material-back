import pathlib
import tempfile
import os
from os.path import basename
from uuid import uuid4
from xml.dom import minidom
from zipfile import ZipFile

from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from vectors.models import Vector
from vectors.serializers import SuggestionSerializer
from vectors.services import taiga as taiga_services
from vectors.services import images as images_services


class Download(APIView):
    def get(self, request):
        # parse params
        ok, errors = self._parse_params(request)
        if not ok:
            response = Response({'errors': errors}, status=400)
            return response

        # get params
        img_format = request.query_params.get('img_format')
        suggested = request.query_params.get('suggested', False)
        new_stroke = request.query_params.get('stroke')
        new_fill = request.query_params.get('fill')
        size = float(request.query_params.get('size', '0'))

        # get vectors
        queryset = Vector.objects

        # filter by img format
        if img_format == 'gif':
            if suggested:
                queryset = queryset.exclude(colored_gif="").exclude(colored_gif__isnull=True)
            else:
                queryset = queryset.exclude(gif="").exclude(gif__isnull=True)
        elif img_format != 'both':
            queryset = queryset.exclude(svg="").exclude(svg__isnull=True)

        # filter by tags
        if 'tags' in request.query_params:
            tags = request.query_params['tags'].split(',')
            if 'all' in tags:
                queryset = queryset.all()
            else:
                for tag in tags:
                    queryset = queryset.filter(tags__name=tag)

        else: # id in request.query_params
            vector_id = request.query_params['id']
            queryset = queryset.filter(id=vector_id)

        vectors = queryset.distinct()

        if not vectors:
            response = Response({'error': 'there are no vectors with these params'}, status=400)
            return response

        # prepare bulk/zip
        if 'tags' in request.query_params:
            zip_name = f'{"_".join(tags)}.zip'
            with tempfile.TemporaryDirectory() as directory:
                zip_file_name = f'{directory}/{zip_name}'

                # si el formato es svg
                if img_format == 'svg':
                    # por cada vector, convertirlo en vector editado en la carpeta temporal
                    for vector in vectors:
                        if suggested:
                            if vector.colored_svg:
                                images_services.customize_vector(vector.colored_svg, directory, None, None)
                            else:
                                images_services.customize_vector(vector.svg, directory, vector.stroke_color, vector.fill_color)
                        else:
                            images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)

                    # crear un zip con todos los svgs
                    svgs = pathlib.Path(directory).glob('*.svg')
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        for svg in svgs:
                            zipfile.write(str(svg), basename(svg.name))

                # si el formato es png
                elif img_format == 'png':
                    # por cada vector, convertirlo en vector editado en la carpeta temporal
                    for vector in vectors:
                        if suggested:
                            if vector.colored_svg:
                                images_services.customize_vector(vector.colored_svg, directory)
                            else:
                                images_services.customize_vector(vector.svg, directory, vector.stroke_color, vector.fill_color)
                        else:
                            images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)

                    # por cada vector en la carpeta, exportarlo a PNG
                    svgs = pathlib.Path(directory).glob('*.svg')
                    for svg in svgs:
                        images_services.export_to_png(svg, size)

                    # crear un zip con todos los pngs de la carpeta
                    pngs = pathlib.Path(directory).glob('*.png')
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        for png in pngs:
                            zipfile.write(str(png), basename(png.name))

                # si el formato es both (png+svg+gif)
                elif img_format == 'both':
                    # por cada vector con svg, convertirlo en vector editado en la carpeta temporal
                    for vector in vectors.exclude(svg="").exclude(svg__isnull=True):
                        if suggested:
                            if vector.colored_svg:
                                images_services.customize_vector(vector.colored_svg, directory)
                            else:
                                images_services.customize_vector(vector.svg, directory, vector.stroke_color, vector.fill_color)
                        else:
                            images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)

                    # por cada svg en la carpeta, exportarlo a PNG
                    svgs = pathlib.Path(directory).glob('*.svg')
                    for svg in svgs:
                        images_services.export_to_png(svg, size)

                    # por cada vector con gif
                    gif_vectors = (vectors
                        .exclude(gif="", colored_gif="")
                        .exclude(gif__isnull=True, colored_gif__isnull=True))

                    for vector in gif_vectors:
                        if suggested:
                            field = vector.colored_gif if vector.colored_gif else vector.gif
                        else:
                            field = vector.gif if vector.gif else vector.colored_gif

                        with (
                            open(f'{directory}/{field.name}', 'wb') as newfile,
                            open(field.file.name, 'rb') as giffile
                        ):
                            newfile.write(giffile.read())

                    # crear un zip con todos los svgs y pngs de la carpeta
                    imgs = pathlib.Path(directory).glob('*.[svg png gif]*')
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        for img in imgs:
                            zipfile.write(str(img), basename(img.name))

                with open(zip_file_name, 'rb') as f:
                    zip_file = f.read()
                    response = HttpResponse(zip_file, content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
                    return response

        # just one file
        elif 'id' in request.query_params:
            vector = vectors[0]

            with tempfile.TemporaryDirectory() as directory:
                if img_format == 'svg':
                    if suggested:
                        if vector.colored_svg:
                            svg = vector.colored_svg
                            path = svg.path
                        else:
                            images_services.customize_vector(vector.svg, directory, vector.stroke_color, vector.fill_color)
                            svg = next(pathlib.Path(directory).glob('*.svg'))
                            path = str(svg)
                    else:
                        images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)
                        svg = next(pathlib.Path(directory).glob('*.svg'))
                        path = str(svg)

                    with open(path, 'rb') as f:
                        response_file = f.read()
                        response = HttpResponse(response_file, content_type='image/svg+xml')
                        response['Content-Disposition'] = f'attachment; filename="{svg.name}"'
                        return response

                elif img_format == 'png':
                    if suggested and vector.colored_svg:
                        images_services.customize_vector(vector.colored_svg, directory)
                    else:
                        images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)

                    svg = next(pathlib.Path(directory).glob('*.svg'))
                    new_name = svg.name.replace('svg', 'png')

                    images_services.export_to_png(svg, size)
                    returning_file = next(pathlib.Path(directory).glob('*.png'))
                    with open(returning_file, 'rb') as f:
                        response_file = f.read()
                        response = HttpResponse(response_file, content_type='image/png')
                        response['Content-Disposition'] = f'attachment; filename="{new_name}"'
                        return response

                # si el formato es gif
                elif img_format == 'gif':
                    gif = vector.colored_gif if suggested and vector.colored_gif else vector.gif
                    path = gif.path

                    with open(path, 'rb') as f:
                        response_file = f.read()
                        response = HttpResponse(response_file, content_type='image/gif')
                        response['Content-Disposition'] = f'attachment; filename="{gif.name}"'
                        return response

                # si el formato es both (png+svg)
                elif img_format == 'both':
                    svg = png = gif = None

                    if vector.svg:
                        # obtener el svg
                        if suggested:
                            if vector.colored_svg:
                                images_services.customize_vector(vector.colored_svg, directory)
                            else:
                                images_services.customize_vector(vector.svg, directory, vector.stroke_color, vector.fill_color)
                        else:
                            images_services.customize_vector(vector.svg, directory, new_stroke, new_fill)
                        svg = next(pathlib.Path(directory).glob('*.svg'))

                        # generar el png
                        images_services.export_to_png(svg, size)
                        png = next(pathlib.Path(directory).glob('*.png'))

                    if vector.gif or vector.colored_gif:
                        gif = vector.colored_gif.file if suggested and vector.colored_gif else vector.gif.file

                    # crear un zip con el svg, el png y el gif
                    zip_name = f"{vector.name.replace(' ', '_')}.zip"
                    zip_file_name = f'{directory}/{zip_name}'
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        if svg:
                            zipfile.write(str(svg), basename(svg.name))
                        if png:
                            zipfile.write(str(png), basename(png.name))
                        if gif:
                            zipfile.write(str(gif), basename(gif.name))

                    with open(zip_file_name, 'rb') as f:
                        zip_file = f.read()
                        response = HttpResponse(zip_file, content_type='application/zip')
                        response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
                        return response

    def _parse_params(self, request):
        errors = []
        ok = True
        if 'tags' not in request.query_params and 'id' not in request.query_params:
            errors.append('tags or id are mandatory')
            ok = False
        elif 'tags' in request.query_params and 'id' in request.query_params:
            errors.append('tags or id, only one of them')
            ok = False

        if 'img_format' not in request.query_params:
            errors.append('img_format is mandatory')
            ok = False
        else:
            img_format = request.query_params.get('img_format')
            if img_format not in ['png', 'svg', 'gif', 'both']:
                errors.append('incorrect img_format: svg or png')
                ok = False
            suggested = request.query_params.get('suggested')
            new_stroke = request.query_params.get('stroke')
            new_fill = request.query_params.get('fill')
            size = request.query_params.get('size', None)
            if size is None and img_format in ["png"]:
                errors.append('size param is needed for this format')
                ok = False
            if size:
                try:
                    float(size)
                except ValueError:
                    errors.append('size must be a valid number')
                    ok = False

        return ok, errors


class Suggestion(CreateAPIView):
    serializer_class = SuggestionSerializer
    # throttle_classes = []

    def perform_create(self, serializer):
        taiga_services.create_suggestion(serializer.data["suggestion"])

