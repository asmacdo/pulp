"""
Each model also requires a ViewSet so that they may be handled by the API. Again, inherit the
matching base class from `pulp.app.viewsets`. `endpoint_name` should by convention match the type
of the content returned by the queryset.
"""
from pulp.app import models, serializers, viewsets

from pulp.app.tests.testapp.models import TestContent, TestImporter
from pulp.app.tests.testapp.serializers import (TestContentSerializer, TestImporterSerializer,
                                                TestCreateImporterSerializer)

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

    def create(self, request, *args, **kwargs):
        """
        Override create so that we can use a serializer that has a repository field.
        """
        repo = models.Repository.objects.filter(name=kwargs['repo_name'])[0]
        repo_href = serializers.RepositoryRelatedField().get_url(
            repo, 'repositories-detail', request, None
        )
        request.data.update(repository=repo_href)
        create_serializer = TestCreateImporterSerializer(data=request.data,
                                                         context={'request': request})
        create_serializer.is_valid(raise_exception=True)
        self.perform_create(create_serializer)
        headers = self.get_success_headers(create_serializer)
        return Response(create_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
