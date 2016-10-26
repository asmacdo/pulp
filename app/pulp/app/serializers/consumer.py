from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import NotesKeyValueRelatedField, PulpModelSerializer


class ConsumerSerializer(PulpModelSerializer):
    _href = serializers.HyperlinkedIdentityField(
        view_name='consumers-detail',
        lookup_field='name',
    )

    name = serializers.CharField(
        help_text="The consumer common name."
    )

    description = serializers.CharField(
        help_text="An optional description.",
        required=False
    )

    notes = NotesKeyValueRelatedField()

    publishers = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='publishers-detail'
    )

    class Meta:
        model = models.Consumer
        fields = PulpModelSerializer.Meta.fields + ('name', 'description', 'notes')
