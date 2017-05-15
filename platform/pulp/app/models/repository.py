"""
Repository related Django models.
"""
from django.db import models
from django.utils import timezone

from pulp.app.models import Model, Notes, Scratchpad, MasterModel, GenericKeyValueRelation


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

        feed_url (models.TextField): The URL of an external content source.
        validate (models.BooleanField): Validate the imported context.
        ssl_ca_certificate (models.TextField): A PEM encoded CA certificate used to validate the
            server certificate presented by the external source.
        ssl_client_certificate (models.TextField): A PEM encoded client certificate used
            for authentication.
        ssl_client_key (models.TextField): A PEM encoded private key used for authentication.
        ssl_validation (models.BooleanField): Indicates whether SSL peer validation
            must be performed.
        proxy_url (models.TextField): The optional proxy URL.
            Format: scheme://user:password@host:port
        basic_auth_user (models.TextField): The user used in HTTP basic authentication.
        basic_auth_password (models.TextField): The password used in HTTP basic authentication.
        download_policy (models.TextField): The policy for downloading content.
        last_sync (models.DatetimeField): When the last successful synchronization occurred.

    Relations:

        scratchpad (GenericKeyValueRelation): Arbitrary information stashed by the importer.
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

    ssl_ca_certificate = models.TextField(blank=True)
    ssl_client_certificate = models.TextField(blank=True)
    ssl_client_key = models.TextField(blank=True)
    ssl_validation = models.BooleanField(default=True)

    proxy_url = models.TextField(blank=True)

    basic_auth_user = models.TextField(blank=True)
    basic_auth_password = models.TextField(blank=True)

    download_policy = models.TextField(choices=DOWNLOAD_POLICIES)
    last_sync = models.DateTimeField(blank=True, null=True)

    scratchpad = GenericKeyValueRelation(Scratchpad)

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


class RepositoryVersion(Model):
    """
    A version of a repository's content set.

    Fields:
        num (models.PositiveIntegerField): A positive integer that uniquely identifies a version
            of a specific repository. Each new version for a repo should have this field set to
            1 + the most recent version.
        created (models.DateTimeField): When the version was created.
        action  (models.TextField): The action that produced the version.

    Relations:

        repository (models.ForeignKey): The associated repository.
    """
    SYNC = 'sync'
    PUBLISH = 'publish'
    COPY = 'copy'
    UPLOAD = 'upload'
    ACTIONS = (
        (SYNC, 'Sync'),
        (PUBLISH, 'Publish'),
        (COPY, 'Copy'),
        (UPLOAD, 'Upload'),
    )

    repository = models.ForeignKey(Repository)
    num = models.PositiveIntegerField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    action = models.TextField(choices=ACTIONS)

    class Meta:
        default_related_name = 'versions'
        unique_together = ('repository', 'num')

    def content(self):
        """
        Returns:

            QuerySet: The Content objects that are related to this version.
        """
        relationships = RepositoryContent.objects.filter(
            repository=self.repository, vadded__num__lte=self.num).exclude(
            vremoved__num__lte=self.num
        )
        # Surely there is a better way to access the model. Maybe it should be in this module.
        content_model = self.repository.content.model
        # This causes a SQL subquery to happen. There may be more efficient SQL, but this is
        # at least correct.
        return content_model.objects.filter(repositorycontent__in=relationships)


class RepositoryContent(Model):
    """
    Association between a repository and its contained content.


    Relations:

        content (models.ForeignKey): The associated content.
        repository (models.ForeignKey): The associated repository.
        vadded (models.ForeignKey): A version in which the content was added to the repository.
        vremoved (models.ForeignKey): The next version following vadded where the content was
            removed from the repository. This may be null.
    """
    content = models.ForeignKey('Content', on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    vadded = models.ForeignKey(RepositoryVersion, related_name='added_content')
    vremoved = models.ForeignKey(RepositoryVersion, null=True, related_name='removed_content')

    class Meta:
        default_related_name = 'repositorycontent'
        unique_together = ('repository', 'content', 'vadded')

