from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from pulpcore.app.apps import pulp_plugin_configs
from rest_framework_nested.relations import NestedHyperlinkedRelatedField,\
    NestedHyperlinkedIdentityField

# a little cache so viewset_for_model doesn't have iterate over every app every time
_model_viewset_cache = {}


# based on their name, viewset_for_model and view_name_for_model look like they should
# live over in the viewsets namespace, but these tools exist for serializers, which are
# depended on by viewsets. They're defined here because they're used here, and to avoid
# odd import dependencies.
def viewset_for_model(model_obj):
    """
    Given a Model instance or class, return the registered ViewSet for that Model
    """
    # model_obj can be an instance or class, force it to class
    model_class = model_obj._meta.model
    if model_class in _model_viewset_cache:
        return _model_viewset_cache[model_class]

    # cache miss, fill in the cache while we look for our matching viewset
    model_viewset = None
    # go through the viewset registry to find the viewset for the passed-in model
    for app in pulp_plugin_configs():
        for model, viewset in app.named_viewsets.items():
            _model_viewset_cache.setdefault(model, viewset)
            if model is model_class:
                model_viewset = viewset
                break
        if model_viewset is not None:
            break

    if model_viewset is None:
        raise LookupError('Could not determine ViewSet base name for model {}'.format(
            model_class))

    return viewset


def view_name_for_model(model_obj, view_action):
    """
    Given a Model instance or class, return the correct view name for that ViewSet view.

    This is the "glue" that generates view names dynamically based on a model object.

    Args:
        model_obj (pulpcore.app.models.Model): a Model that should have a ViewSet
        view_action (str): name of the view action as expected by DRF. See their docs for details.

    Returns:
        str: view name for the correct ViewSet

    Raises:
        LookupError: if no ViewSet is found for the Model
    """
    # Import this here to prevent out-of-order plugin discovery
    from pulpcore.app.urls import all_routers

    viewset = viewset_for_model(model_obj)

    # return the complete view name, joining the registered viewset base name with
    # the requested view method.
    for router in all_routers:
        for pattern, registered_viewset, base_name in router.registry:
            if registered_viewset is viewset:
                return '-'.join((base_name, view_action))
    raise LookupError('view not found')


# Defined here instead of generic.py to avoid potential circular imports issues,
# since this is used by ModelSerializer
class GenericKeyValueRelatedField(serializers.DictField):
    """
    Base class for GenericKeyValueMutableMapping model implementations.

    These work by representing the "mapping" attribute of these fields using DRF's DictField,
    with all values to be stored as text.

    You can store anything you want in here, as long as it's a string.
    """
    child = serializers.CharField()

    def to_representation(self, value):
        # The field being represented isn't a dict, but the mapping attr is,
        # so value.mapping is the actual value that needs to be represented.
        return super(GenericKeyValueRelatedField, self).to_representation(value.mapping)


class ModelSerializer(serializers.HyperlinkedModelSerializer):
    """Base serializer for use with :class:`pulpcore.app.models.Model`

    This ensures that all Serializers provide values for the '_href` field, and
    adds read/write support for :class:`pulpcore.app.serializers.GenericKeyValueRelatedField`
    nested fields.
    """

    class Meta:
        fields = ('_href',)

    def create(self, validated_data):
        # pop related fields out of validated data
        generic_field_mappings = self._generic_field_mappings(validated_data)

        instance = super(ModelSerializer, self).create(validated_data)

        # populate related fields
        self._populate_generic_fields(instance, generic_field_mappings)

        return instance

    def update(self, instance, validated_data):
        # pop related fields out of validated data
        generic_field_mappings = self._generic_field_mappings(validated_data)

        instance = super(ModelSerializer, self).update(instance, validated_data)

        # populate related fields
        self._populate_generic_fields(instance, generic_field_mappings)

        return instance

    def _generic_field_mappings(self, validated_data):
        # Strip generic k/v pairs out of validated data and return them.
        generic_mappings = {}
        for field_name, field in self.get_fields().items():
            if isinstance(field, GenericKeyValueRelatedField):
                try:
                    generic_mappings[field_name] = validated_data.pop(field_name)
                except KeyError:
                    pass
        return generic_mappings

    def _populate_generic_fields(self, instance, field_mappings):
        for field_name, mapping in field_mappings.items():
            field = getattr(instance, field_name)
            field.mapping.replace(mapping)

class NestedModelSerializer(ModelSerializer):
    """
    This class allows a serializer to determine the value for a nested parent object from the url
    of a request.

    These serializers must be used by a NestedNamedModelViewSet, which implements the required `get_parent_field_and_object` function.

    Example:

    class NumberSerializer(NestedModelSerializer):
        letter = foreignkeyfield()

    POST letters/a/numbers number=one Creates a number object, one, which will have an attribute one.letter == 'a'
    """

    def to_internal_value(self, *args, **kwargs):
        # super().to_internal_value will validate all writable fields and populate serializer.data
        validated_data = super().to_internal_value(*args, **kwargs)
        # nested parent fields should be read_only (so they don't accept args that are ignored)
        # instead, validate the parent based on the parent url and add it to the validated data.
        validated_data.update(self.writable_nested_parent_url_to_internal())
        return validated_data

    def writable_nested_parent_url_to_internal(self):
        url_parents = OrderedDict()
        for field in self.fields.values():
            # Writable nested parent objects must be read only (the parent is determined by the url kwargs)
            if (getattr(field, 'href_writable', False)):
                # Use the original viewset to retrieve or 404 the parent object implied by the request url
                parent_field, parent_obj = self.context['view'].get_parent_field_and_object()
                url_parents[parent_field] = parent_obj
        return url_parents


class MasterModelSerializer(ModelSerializer):
    """
    Base serializer for all Master/Detail Models.

    When subclassing this, all subclasses should explicitly inherit the fields of their parent
    in their Meta options class. For example:

        class MasterSerializer(MasterModelSerializer):
            foo = SerializerField()

            class Meta:
                fields = MasterModelSerializer.Meta.fields + ('foo',)

        class DetailSerializer(MasterSerializer):
            bar = SerializerField()

            class Meta:
                fields = MasterSerializer.Meta.fields + ('bar',)

    This ensures that fields are represented consistently throughout the API, and Detail Model
    types are cast down before representation.

    Other Meta attributes, such as `filter_fields`, should also be inherited in this way
    as-needed.

    """
    type = serializers.CharField(read_only=True)

    class Meta:
        fields = ModelSerializer.Meta.fields + ('type',)

    def to_representation(self, instance):
        """
        Represent a cast Detail instance as a dict of primitive datatypes
        """

        # This is very similar to DRF's default to_representation implementation in
        # ModelSerializer, but makes sure to cast Detail instances and use the correct
        # serializer for rendering so that all detail fields are included.
        ret = OrderedDict()

        instance = instance.cast()
        viewset = viewset_for_model(instance)
        fields = viewset.serializer_class(context=self._context)._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class MatchingNullViewName(object):
    """Object that can be used as the default view name for detail fields

    This is needed to bypass a view name check done in DRF's to_internal_value method
    that checks that the view name for the incoming data matches the view name it expects
    for the object being represented. Since we don't know the view name for that object
    until it's been cast, and it doesn't get cast until get_object is called, and this
    check happens immediately before get_object is called, this check is probitive to our
    implementation. Setting the default view_name attr of a Detail related or identity
    field to an instance of this class should ensure the the view_name attribute of one
    of these related fields is equal to any view name it's compared to, bypassing DRF's
    view_name matching check.
    """
    def __eq__(self, other):
        return True


class _DetailFieldMixin:
    """Mixin class containing code common to DetailIdentityField and DetailRelatedField"""
    def __init__(self, view_name=None, **kwargs):
        if view_name is None:
            # set view name to prevent a DRF assertion that view_name is not None
            # Anything that accesses self.view_name after __init__
            # needs to have it set before being called. Unfortunately, a model instance
            # is required to derive this value, so we can't make a view_name property.
            view_name = MatchingNullViewName()
        super(_DetailFieldMixin, self).__init__(view_name, **kwargs)

    def _view_name(self, obj):
        # this is probably memoizeable based on the model class if we want to get cachey
        try:
            obj = obj.cast()
        except AttributeError:
            # The normal message that comes up here is unhelpful, so do like other DRF
            # fails do and be a little more helpful in the exception message.
            msg = ('Expected a detail model instance, not {}. Do you need to add "many=True" to '
                   'this field definition in its serializer?').format(type(obj))
            raise ValueError(msg)
        return view_name_for_model(obj, 'detail')

    def get_url(self, obj, view_name, *args, **kwargs):
        # ignore the passed in view name and return the url to the cast unit, not the generic unit
        view_name = self._view_name(obj)
        return super(_DetailFieldMixin, self).get_url(obj, view_name, *args, **kwargs)


class DetailIdentityField(_DetailFieldMixin, serializers.HyperlinkedIdentityField):
    """IdentityField for use in the _href field of Master/Detail Serializers

    When using this field on a Serializer, it will automatically cast objects to their Detail type
    base on the Serializer's Model before generating URLs for them.

    Subclasses must indicate the Master model they represent by declaring a queryset
    in their class body, usually <MasterModelImplementation>.objects.all().
    """


class DetailRelatedField(_DetailFieldMixin, serializers.HyperlinkedRelatedField):
    """RelatedField for use when relating to Master/Detail models

    When using this field on a Serializer, relate it to the Master model in a
    Master/Detail relationship, and it will automatically cast objects to their Detail type
    before generating URLs for them.

    Subclasses must indicate the Master model they represent by declaring a queryset
    in their class body, usually <MasterModelImplementation>.objects.all().
    """
    def get_object(self, *args, **kwargs):
        # return the cast object, not the generic contentunit
        return super(DetailRelatedField, self).get_object(*args, **kwargs).cast()

    def use_pk_only_optimization(self):
        """
        If the lookup field is `pk`, DRF substitutes a PKOnlyObject as an optimization. This
        optimization breaks with Detail fields like this one which need access to their Meta
        class to get the relevant `view_name`.
        """
        return False


class DetailNestedHyperlinkedRelatedField(_DetailFieldMixin, NestedHyperlinkedRelatedField):
    """
    For use with nested viewsets of master/detail models
    """
    # TODO(asmacdo) is this still necessary?
    pass


class WritableNestedUrlRelatedField(DetailNestedHyperlinkedRelatedField):
    """
    This field is determined by the requst url and the parent object found by using the url kwargs
    and the parent lookup_kwargs.

    It is writable, but does not accept request parameters.
    """
    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        self.href_writable = True
        super().__init__(*args, **kwargs)

    # Is this necessary? Why?
    def get_object(self, view_name, view_args, view_kwargs):
        qs = self.get_queryset()
        if self.parent_lookup_kwargs:
            filters = {}
            for key, lookup in self.parent_lookup_kwargs.items():
                filters[lookup] = view_kwargs.pop(key)
            qs = qs.filter(**filters)
        return qs.get(**view_kwargs).cast()


class DetailNestedHyperlinkedIdentityField(_DetailFieldMixin, NestedHyperlinkedIdentityField):
    """
    For use with nested viewsets of master/detail models
    """
    pass
