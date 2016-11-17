from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import base, DetailRelatedField


class ContentRelatedField(DetailRelatedField):
    """
    Serializer Field for use when relating to Content Detail Models
    """
    queryset = models.Content.objects.all()

    def _view_name(self, obj):
        obj = models.Content.objects.filter(pk=obj.pk)[0].cast()
        return base.view_name_for_model(obj, 'detail')


class RepositoryRelatedField(serializers.HyperlinkedRelatedField):
    """
    A serializer field with the correct view_name and lookup_field to link to a repository.
    """
    view_name = 'repositories-detail'
    lookup_field = 'name'
    queryset = models.Repository.objects.all()
