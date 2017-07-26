"""
Repository related Django models.
"""
from django.db import models
from django.utils import timezone

from pulpcore.app.models import Model, Notes, Scratchpad, MasterModel, GenericKeyValueRelation
from pulpcore.app.models.storage import TLSLocation


class Repository(Model):
    """
    Collection of content.

    Fields:

        name (models.TextField): The repository name.
        description (models.TextField): An optional description.
        last_content_added (models.DateTimeField): When content was last added.
        last_content_removed (models.DatetimeField): When content was last removed.

    Relations:

        scratchpad (GenericKeyValueRelation): Arbitrary information stashed on the repository.
        notes (GenericKeyValueRelation): Arbitrary repository properties.
        content (models.ManyToManyField): Associated content.
    """
    name = models.TextField(db_index=True, unique=True)
    description = models.TextField(blank=True)

    last_content_added = models.DateTimeField(blank=True, null=True)
    last_content_removed = models.DateTimeField(blank=True, null=True)

    scratchpad = GenericKeyValueRelation(Scratchpad)
    notes = GenericKeyValueRelation(Notes)

    content = models.ManyToManyField('Content', through='RepositoryContent',
                                     related_name='repositories')

    class Meta:
        verbose_name_plural = 'repositories'

    @property
    def content_summary(self):
        """
        The contained content summary.

        :return: A dict of {<type>: <count>}
        :rtype:  dict
        """
        mapping = self.content.values('type').annotate(count=models.Count('type'))
        return {m['type']: m['count'] for m in mapping}

    def natural_key(self):
        """
        Get the model's natural key.

        :return: The model's natural key.
        :rtype: tuple
        """
        return (self.name,)


class ContentAdaptor(MasterModel):
    """
    An Abstract model for objects that import or publish content.

    Fields:

        name (models.TextField): The ContentAdaptor name.
        last_updated (models.DatetimeField): When the adaptor was last updated.

    Relations:

        repository (models.ForeignKey): The associated repository.
    """
    name = models.TextField(db_index=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = ('repository', 'name')

    def natural_key(self):
        """
        Get the model's natural key.

        Returns:

            tuple: The model's natural key.
        """
        return (self.repository, self.name)


class Importer(ContentAdaptor):
    """
    A content importer.

    Fields:

        name (models.TextField): Name of this importer, unique together with repository name.
        feed_url (models.TextField): The URL of an external content source.

        validate (models.BooleanField): If true, the plugin will validate the imported context.
        ssl_ca_certificate (models.TextField): A PEM encoded CA certificate used to validate the
            server certificate presented by the external source.
        ssl_client_certificate (models.TextField): A PEM encoded client certificate used
            for authentication.
        ssl_client_key (models.TextField): A PEM encoded private key used for authentication.
        ssl_validation (models.BooleanField): If true, SSL peer validation must be performed.
        proxy_url (models.TextField): The optional proxy URL.
            Format: scheme://user:password@host:port
        username (models.TextField): The username to be used for authentication when syncing.
        password (models.TextField): The password to be used for authentication when syncing.
        download_policy (models.TextField): Contains the downloading policy name.
            This is a choice of three options:
            - immediate (default): The sync task is not complete until downloading is finished.
            - background: Downloading is started by the sync but occurs in the background. The sync
                          task completes before downloading is complete.
            - on_demand: Sync tasks update repository metadata but does not download content.
                         Downloads occur on demand as driven by client requests for content.

        sync_mode: (models.TextField): Two choices 'additive' and 'mirror':
            - additive (default) - all remote content is added to the local repository on sync. During sync no content is removed from the local repository.
            - mirror - the local content will mirror the remote content exactly, removing local content if not also present in the remote content.

        last_updated (models.DatetimeField): Datetime of the last update of the importer.
        last_synced (models.DatetimeField): Datetime of the last importer sync.

    """
    TYPE = 'importer'

    # Download Policies
    IMMEDIATE = 'immediate'
    ON_DEMAND = 'on_demand'
    BACKGROUND = 'background'
    DOWNLOAD_POLICIES = (
        (IMMEDIATE, 'Download Immediately'),
        (ON_DEMAND, 'Download On Demand'),
        (BACKGROUND, 'Download In Background'))
    # Sync modes
    ADDITIVE = 'additive'
    MIRROR = 'mirror'
    SYNC_MODES = (
        (ADDITIVE, 'Add new content, keep content that was removed upstream.')
        (MIRROR, 'Add new content, if content was removed upstream, remove it.'))

    # Setting this with "unique=True" will trigger a model validation warning, telling us that we
    # should use a OneToOneField here instead. While it is correct, doing it this way makes it
    # easy to allow multiple importers later: Move the 'repository' field from Importer and
    # Publisher to ContentAdaptor (without unique=True). This should make any migration that
    # allows multiple importers to be simple, since all that's needed is removing a constraint.
    # Using a OneToOneField here would break forward-compatibility with the idea of having
    # multiple importers associated with a Repository, since this exposes a ManyRelatedManager
    # on Repository with name "importers", and a OneToOneField would instead expose the single
    # related Importer instance.
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, unique=True)

    feed_url = models.TextField()
    validate = models.BooleanField(default=True)

    ssl_ca_certificate = models.FileField(
        blank=True, upload_to=TLSLocation('ca.pem'), max_length=255)
    ssl_client_certificate = models.FileField(
        blank=True, upload_to=TLSLocation('certificate.pem'), max_length=255)
    ssl_client_key = models.FileField(
        blank=True, upload_to=TLSLocation('key.pem'), max_length=255)

    ssl_validation = models.BooleanField(default=True)

    proxy_url = models.TextField(blank=True)

    username = models.TextField(blank=True)
    password = models.TextField(blank=True)

    download_policy = models.TextField(choices=DOWNLOAD_POLICIES)
    sync_mode = models.TextField(choices=SYNC_MODES)

    last_synced = models.DateTimeField(blank=True, null=True)

    class Meta(ContentAdaptor.Meta):
        default_related_name = 'importers'


class Publisher(ContentAdaptor):
    """
    A content publisher.

    Fields:

        auto_publish (models.BooleanField): Indicates that the adaptor may publish automatically
            when the associated repository's content has changed.
        relative_path (models.TextField): The (relative) path component of the published url.
        last_published (models.DatetimeField): When the last successful publish occurred.

    Relations:

    """
    TYPE = 'publisher'

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    auto_publish = models.BooleanField(default=True)
    relative_path = models.TextField(blank=True)
    last_published = models.DateTimeField(blank=True, null=True)

    class Meta(ContentAdaptor.Meta):
        default_related_name = 'publishers'


class RepositoryContent(Model):
    """
    Association between a repository and its contained content.

    Fields:

        created (models.DatetimeField): When the association was created.

    Relations:

        content (models.ForeignKey): The associated content.
        repository (models.ForeignKey): The associated repository.
    """
    content = models.ForeignKey('Content', on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Save the association.
        """
        self.repository.last_content_added = timezone.now()
        self.repository.save()
        super(RepositoryContent, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete the association.
        """
        self.repository.last_content_removed = timezone.now()
        self.repository.save()
        super(RepositoryContent, self).delete(*args, **kwargs)
