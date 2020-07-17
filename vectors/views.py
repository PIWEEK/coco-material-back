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
        if 'tags' not in request.query_params and 'id' not in request.query_params:
            response = Response({'error': 'tags or id are mandatory'}, status=400)
            return response
        if 'tags' in request.query_params and 'id' in request.query_params:
            response = Response({'error': 'tags or id, only one of them'}, status=400)
            return response

        queryset = Vector.objects
        if 'tags' in request.query_params:
            tags = request.query_params['tags'].split(',')
            for tag in tags:
                queryset = queryset.filter(tags__name=tag)
        else: # id in request.query_params
            vector_id = request.query_params['id']
            queryset = queryset.filter(id=vector_id)

        vectors = queryset.distinct()
        if not vectors:
            response = Response({'error': 'there are no vectors with these tags'}, status=400)
            return response

        if len(vectors) == 1:
            zip_file_name = f'{vectors[0].svg.name}.zip'
        else:
            zip_file_name = f'{"_".join(tags)}.zip'

        img_format = request.query_params.get('img_format', 'svg')
        if img_format not in ['png', 'svg']:
            response = Response({'error': 'incorrect format, png or svg'}, status=400)
            return response

        if img_format == 'png':
            new_stroke = request.query_params.get('stroke')
            new_fill = request.query_params.get('fill')
            size = int(request.query_params.get('size'))
            if not (new_stroke and new_fill and size):
                response = Response({'error': 'png params missing'}, status=400)
                return response

        # zip
        with tempfile.TemporaryDirectory() as directory:
            zip_name = f'{directory}/{zip_file_name}'

            if img_format == 'svg':
                with ZipFile(zip_name, 'w') as zipfile:
                    for vector in vectors:
                        zipfile.write(vector.svg.path, basename(vector.svg.name))
            elif img_format == 'png':
                # por cada vector, convertirlo en vector modificado en la carpeta temporal
                for vector in vectors:
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

                # por cada vector en la carpeta, exportarlo a PNG
                svgs = pathlib.Path(directory).glob('*.svg')
                for svg in svgs:
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

                # crear un zip con todos los pngs de la carpeta
                pngs = pathlib.Path(directory).glob('*.png')
                with ZipFile(zip_name, 'w') as zipfile:
                    for png in pngs:
                        zipfile.write(str(png), basename(png.name))

            response = None
            with open(zip_name, 'rb') as f:
                zip_file = f.read()
                response = HttpResponse(zip_file, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'

            return response
