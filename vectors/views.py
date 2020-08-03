import pathlib
import tempfile
import os
from os.path import basename
from uuid import uuid4
from xml.dom import minidom
from zipfile import ZipFile

import cairosvg
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
import svgutils.transform as sg

from vectors.models import Vector


class Download(APIView):

    def get(self, request):
        # parse params
        ok, errors = self._parse_params(request)
        if not ok:
            response = Response({'errors': errors}, status=400)
            return response

        # get params
        img_format = request.query_params.get('img_format')
        if img_format == 'png':
            new_stroke = request.query_params.get('stroke')
            new_fill = request.query_params.get('fill')
            size = int(request.query_params.get('size'))

        # get vectors
        queryset = Vector.objects
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

                # si el formato es svg, directamente crear un zip con todos los vectores que hacen falta
                if img_format == 'svg':
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        for vector in vectors:
                            zipfile.write(vector.svg.path, basename(vector.svg.name))

                # si el formato es png
                elif img_format == 'png':
                    # por cada vector, convertirlo en vector editado en la carpeta temporal
                    for vector in vectors:
                        self._edit_vector(vector, directory, new_stroke, new_fill)

                    # por cada vector en la carpeta, exportarlo a PNG
                    svgs = pathlib.Path(directory).glob('*.svg')
                    for svg in svgs:
                        self._export_to_png(svg, size)

                    # crear un zip con todos los pngs de la carpeta
                    pngs = pathlib.Path(directory).glob('*.png')
                    with ZipFile(zip_file_name, 'w') as zipfile:
                        for png in pngs:
                            zipfile.write(str(png), basename(png.name))

                with open(zip_file_name, 'rb') as f:
                    zip_file = f.read()
                    response = HttpResponse(zip_file, content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
                    return response

        # just one file
        elif 'id' in request.query_params:
            vector = vectors[0]

            if img_format == 'svg':
                with open(f'media/{vector.svg.name}', 'rb') as f:
                    response_file = f.read()
                    response = HttpResponse(response_file, content_type='image/svg+xml')
                    response['Content-Disposition'] = f'attachment; filename="{vector.svg.name}"'
                    return response

            elif img_format == 'png':
                with tempfile.TemporaryDirectory() as directory:
                    self._edit_vector(vector, directory, new_stroke, new_fill)
                    svg = next(pathlib.Path(directory).glob('*.svg'))
                    self._export_to_png(svg, size)
                    returning_file = next(pathlib.Path(directory).glob('*.png'))
                    with open(returning_file, 'rb') as f:
                        new_name = vector.svg.name.replace('svg', 'png')
                        response_file = f.read()
                        response = HttpResponse(response_file, content_type='image/png')
                        response['Content-Disposition'] = f'attachment; filename="{new_name}"'
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
            if img_format not in ['png', 'svg']:
                errors.append('incorrect img_format: svg or png')
                ok = False
            elif img_format == 'png':
                new_stroke = request.query_params.get('stroke')
                new_fill = request.query_params.get('fill')
                size = request.query_params.get('size')
                if not (new_stroke and new_fill and size):
                    errors.append('png params missing')
                    ok = False

        return ok, errors


    def _export_to_png(self, svg, size):
        orig = str(svg)
        fig = sg.fromfile(orig)
        width = float(fig.width[:-2])
        height = float(fig.height[:-2])
        max_size = max(width, height)
        increase_ratio = size / max_size
        new_width = round(width * increase_ratio)
        new_height = round(height * increase_ratio)
        new_name = svg.name.replace('.svg', '.png')
        dest = str(svg.parent / new_name)
        cairosvg.svg2png(url=orig, write_to=dest, parent_width=new_width, parent_height=new_height)


    def _edit_vector(self, vector, directory, new_stroke, new_fill):
        with minidom.parse(vector.svg.path) as dom, open(f'{directory}/{vector.svg.name}', 'w') as newsvg:
            paths = dom.getElementsByTagName('path')
            for path in paths:
                fill = path.getAttribute('fill')
                if fill in ['#030303', '#000000']:
                    fill = f'#{new_stroke}'.replace('#none', 'none')
                else: # fill == fff | ffffff
                    fill = f'#{new_fill}'.replace('#none', 'none')
                path.setAttribute('fill', fill)

            newsvg.write(dom.toxml())
