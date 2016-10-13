from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import NotesKeyValueRelatedField, ModelSerializer


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


class RepositoryGroup(ModelSerializer):
    """
    Pass for now, are we killing the Repo Group?
    """
    pass


class ImporterSerializer(ModelSerializer):
    # _href is normally provided by the base class, but Importers's
    # "name" lookup field means _href must be explicitly declared.
    _href = serializers.HyperlinkedIdentityField(
        view_name='importers-detail',
        lookup_field='name',
    )
    name = serializers.CharField(
        help_text='A name for this importer, unique within the associated repository.'
    )
    last_updated = serializers.DateTimeField(
        help_text='Timestamp of the most recent update of this Importer.',
        read_only=True
    )
    # TODO(asmacdo) I suspect this doesn't need to be here. Or if it does, I just want to show
    # repository.name
    repository = serializers.HyperlinkedRelatedField(read_only=True,
                                                     view_name='repositories-detail')
    feed_url = serializers.CharField(help_text='The URL of an external content source.')
    validate = serializers.BooleanField(help_text='Whether to validate imported content.')
    ssl_ca_certificate = serializers.CharField(
        help_text='A PEM encoded CA certificate used to validate the server '
                  'certificate presented by the external source.'
    )
    ssl_client_certificate = serializers.CharField(
        help_text='A PEM encoded client certificate used for authentication.'
    )
    ssl_client_key = serializers.CharField(
        help_text='A PEM encoded private key used for authentication.'
    )
    ssl_validation = serializers.BooleanField(
        help_text='Indicates whether SSL peer validation must be performed.'
    )
    proxy_url = serializers.CharField(
        help_text='The optional proxy URL. Format: scheme://user:password@host:port'
    )
    basic_auth_user = serializers.CharField(
        help_text='The username to be used in HTTP basic authentication when syncing.'
    )
    basic_auth_password = serializers.CharField(
        help_text='The password to be used in HTTP basic authentication when syncing.'
    )
    max_download_bandwidth = serializers.IntegerField(
        help_text='The max amount of bandwidth used per download (Bps).'
    )
    max_concurrent_downloads = serializers.IntegerField(
        help_text='The number of concurrent downloads permitted.'
    )
    download_policy = serializers.CharField(
        help_text='The policy for downloading content.',
    )
    last_sync = serializers.DateTimeField(
        help_text='Timestamp of the most recent sync.',
        read_only=True
    )


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
