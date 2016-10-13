from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import (ModelSerializer, NotesKeyValueRelatedField,
                                  MasterModelSerializer, RepositoryNestedIdentityField)


class RepositorySerializer(ModelSerializer):
    # _href is normally provided by the base class, but Repository's
    # "name" lookup field means _href must be explicitly declared.
    _href = serializers.HyperlinkedIdentityField(
        view_name='repositories-detail',
        lookup_field='name',
    )
    name = serializers.CharField(
        help_text='A unique name for this repository.',
        write_only=True
    )

    description = serializers.CharField(
        help_text='An optional description.',
        required=False
    )

    last_content_added = serializers.DateTimeField(
        help_text='Timestamp of the most recent addition of content to this repository.',
        read_only=True
    )

    last_content_removed = serializers.DateTimeField(
        help_text='Timestamp of the most recent removal of content to this repository.',
        read_only=True
    )
    notes = NotesKeyValueRelatedField()

    class Meta:
        model = models.Repository
        fields = ModelSerializer.Meta.fields + ('name', 'description', 'notes',
                                                'last_content_added', 'last_content_removed')


class ImporterSerializer(MasterModelSerializer):
    """
    Base class for Importers, this is intended to be subclassed by each plugin.

    Please import from `pulp.app.serializers` rather than from this module directly.

    Every class that inherrits from this class must override the `_href` method with a
    `RepositoryNestedIdentityField` that defines the view_name.

    """
    name = serializers.CharField(
        help_text='A name for this importer, unique within the associated repository.'
    )

    class Meta:
        abstract = True
        fields = MasterModelSerializer.Meta.fields + ('name',)


class ExampleDetailImporterSerializer(ImporterSerializer):
    """
    Example of a Detail serializer that also utilizes nested routes.
    """
    # Content adapters need to use two kwargs because the name is only unique within a
    # repository and alone, `Importer.name` is not enough to uniquely identify it.
    _href = RepositoryNestedIdentityField(view_name='importers-exampletype-detail')

    class Meta:
        model = models.ExampleDetailImporter
        fields = ImporterSerializer.Meta.fields
