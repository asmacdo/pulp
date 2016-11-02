"""
The plugin should implement a serializer for each of the required models and any others that are not
abstract. These serializers should choose the matching base class from `pulp.app.serializers`. Be
sure not to clobber the parent class' field data.
"""
from pulp.app import models
from pulp.app.serializers import (ContentSerializer, ImporterSerializer,
                                  RepositoryNestedIdentityField)
from pulp.app.tests.testapp.models import TestContent, TestImporter

from rest_framework import serializers


class TestContentSerializer(ContentSerializer):
    class Meta:
        fields = ContentSerializer.Meta.fields + ('name',)
        model = TestContent


class TestImporterSerializer(ImporterSerializer):
    """
    Example of a Detail serializer that also utilizes nested routes.
    """
    # Importers and Publishers have a two field natural key (repository and name). We override
    # _href in this case so we can have a special IdentityField to build those nested URLs.
    _href = RepositoryNestedIdentityField(view_name='importers-test-detail')
    queryset = TestImporter.objects.all()

    class Meta:
        model = TestImporter
        fields = ImporterSerializer.Meta.fields


class TestCreateImporterSerializer(TestImporterSerializer):
    repository = serializers.HyperlinkedRelatedField(
        lookup_field='name',
        view_name='repositories-detail',
        queryset=models.Repository.objects.all(),
    )

    class Meta:
        model = TestImporterSerializer.Meta.model
        abstract = True
        fields = TestImporterSerializer.Meta.fields + ('repository',)
