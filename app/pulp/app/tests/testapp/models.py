"""
A plugin is required to implement at least these three models. They should inherrit from these base
classes.
"""
from django.db import models

from pulp.app.models import Content, Importer, Publisher


class TestContent(Content):
    TYPE = 'test'

    name = models.TextField()

    class Meta:
        pass


class TestImporter(Importer):
    TYPE = 'test'

    test_field = models.TextField()

    class Meta(Importer.Meta):
        # It is necessary to override the parent's `unique_together` field because this model is
        # not aware of the fields referenced, but the parent is.
        unique_together = None


class TestPublisher(Publisher):
    TYPE = 'test'

    test_field = models.TextField()

    class Meta:
        pass
