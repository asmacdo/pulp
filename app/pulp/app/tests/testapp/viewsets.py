"""
Each model also requires a ViewSet so that they may be handled by the API. Again, inherit the
matching base class from `pulp.app.viewsets`. `endpoint_name` should by convention match the type
of the content returned by the queryset.
"""
from pulp.app import models, serializers, viewsets

from pulp.app.tests.testapp.models import TestContent, TestImporter
from pulp.app.tests.testapp.serializers import (TestContentSerializer, TestImporterSerializer,
                                                )
"""TODO(asmacdo) second serializer"""
                                                # TestCreateImporterSerializer)

from rest_framework import status
from rest_framework.response import Response


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

    """Parent definition (untested for typos, lives in rest_framework/mixins.py)"""
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status.status.HTTP_201_CREATED, headers=headers)

    """TODO(asmacdo) second serializer"""
    # def create(self, request, *args, **kwargs):
    #     repo = self.get_object()
    #     repo_href = serializers.RepositoryRelatedField().get_url(
    #         repo, 'repositories-detail', request, None
    #     )
    #     request.data.update(repository=repo_href)
    #     create_serializer = TestCreateImporterSerializer(data=request.data)
    #     create_serializer.is_valid(raise_exception=True)
    #     self.perform_create(create_serializer)
    #     headers = self.get_success_headers(create_serializer)
    #     return Response(create_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
