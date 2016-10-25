"""
Each model also requires a ViewSet so that they may be handled by the API. Again, inherit the
matching base class from `pulp.app.viewsets`. `endpoint_name` should by convention match the type
of the content returned by the queryset.
"""
from pulp.app import viewsets

from pulp.app.tests.testapp.models import TestContent, TestImporter
from pulp.app.tests.testapp.serializers import TestContentSerializer, TestImporterSerializer


class TestContentViewSet(viewsets.ContentViewSet):
    endpoint_name = 'test'
    queryset = TestContent.objects.all()
    serializer_class = TestContentSerializer


class TestImporterViewSet(viewsets.ImporterViewSet):
    # The relative url is built using the endpoint name and the parent class's endpoint name, in
    # this case importers/test/.
    endpoint_name = 'test'
    # If the urls are built using a field other than the pk, specify the field with `lookup_field`.
    lookup_field = 'name'

    queryset = TestImporter.objects.all()
    serializer_class = TestImporterSerializer

