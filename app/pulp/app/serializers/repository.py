from rest_framework import serializers
from rest_framework.reverse import reverse

from pulp.app import models
from pulp.app.serializers import (base, NotesKeyValueRelatedField, ModelSerializer,
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


class CustomRelatedField(serializers.HyperlinkedRelatedField):
    view_name = 'importers-detail',
    queryset = models.ExampleDetailImporter.objects.all()

    #TODO(asmacdo) repo.name?
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'repo_name': obj.repository,
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
    _href = CustomRelatedField()
    name = serializers.CharField(
        help_text='A name for this importer, unique within the associated repository.'
    )

    class Meta:
        abstract = True
        fields = MasterModelSerializer.Meta.fields + ('name',)


class PublisherSerializer(ModelSerializer):
    # _href is normally provided by the base class, but Importers's
    # "name" lookup field means _href must be explicitly declared.
    _href = serializers.HyperlinkedIdentityField(
        view_name='publishers-detail',
        lookup_field='name',
    )
    name = serializers.CharField(
        help_text='A name for this publisher, unique within the associated repository.'
    )
    last_updated = serializers.DateTimeField(
        help_text='Timestamp of the most recent update of this Publisher.',
        read_only=True
    )
    # TODO(asmacdo) I suspect this doesn't need to be here. Or if it does, I just want to show
    # repository.name
    repository = serializers.HyperlinkedRelatedField(read_only=True,
                                                     view_name='repositories-detail')

    auto_publish = serializers.BooleanField(
        help_text='Indicates that the adaptor may publish automatically when the associated '
                  'repository\'s content has changed.'
    )
    relative_path = serializers.CharField(
        help_text='The (relative) path component of the published url.'
    )
    last_updated = serializers.DateTimeField(
        help_text='Timestamp of the most publish.',
        read_only=True
    )


class ExampleDetailImporterSerializer(ImporterSerializer):
    _href = base.DetailIdentityField()

    class Meta:
        model = models.ExampleDetailImporter
        fields = ImporterSerializer.Meta.fields
