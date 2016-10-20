from rest_framework import serializers
from rest_framework.reverse import reverse

from pulp.app import models
from pulp.app.serializers import (NotesKeyValueRelatedField, ModelSerializer,
                                  MasterModelSerializer)


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


class CustomRelatedField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'repo_name': obj.repository.name,
            'name': obj.name
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'repository__name': view_kwargs['repo_name'],
            'name': view_kwargs['name']
        }
        return self.get_queryset().get(**lookup_kwargs)


class ImporterSerializer(MasterModelSerializer):
    name = serializers.CharField(
        help_text='A name for this importer, unique within the associated repository.'
    )

    class Meta:
        abstract = True
        fields = MasterModelSerializer.Meta.fields + ('name',)


class ExampleDetailImporterSerializer(ImporterSerializer):
    _href = CustomRelatedField(view_name='importers-exampletype-detail')

    class Meta:
        model = models.ExampleDetailImporter
        fields = ImporterSerializer.Meta.fields
