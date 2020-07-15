from os.path import basename
from uuid import uuid4
from zipfile import ZipFile

from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from vectors.models import Vector


class BulkDownload(APIView):
    def get(self, request):
        if 'tags' not in request.query_params:
            response = Response({'error': 'tags are mandatory'}, status=400)
            return response

        tags = request.query_params['tags'].split(',')
        queryset = Vector.objects
        for tag in tags:
            queryset = queryset.filter(tags__name=tag)

        vectors = queryset.distinct()
        if not vectors:
            response = Response({'error': 'there are no vectors with these tags'}, status=400)
            return response

        zip_name = f'delete/cocomaterial_{uuid4().hex}.zip'
        with ZipFile(zip_name, 'w') as zipfile:
            for vector in vectors:
                zipfile.write(vector.svg.path, basename(vector.svg.name))

        with open(zip_name, 'rb') as f:
            zip_file = f.read()
            response = HttpResponse(zip_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="cocomaterial.zip"'
            return response
