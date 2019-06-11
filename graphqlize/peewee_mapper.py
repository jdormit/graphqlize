"""
Mapping logic for Peewee models
"""
from __future__ import absolute_import

import logging
import peewee
import graphene
from typing import List, Any, Optional

from graphqlize import graphqlize, GraphQLizeException

logger = logging.getLogger('graphqlize.peewee_mapper')

peewee_to_graphene_fields = {
    # TODO support peewee.BareField
    peewee.BigIntegerField: graphene.Int,
    # TODO support peewee.BinaryField
    # TODO support peewee.BlobField
    peewee.BooleanField: graphene.Boolean,
    peewee.CharField: graphene.String,
    # TODO support peewee.DateField
    # TODO support peewee.DateTimeField
    peewee.DecimalField: graphene.Float,
    peewee.DoubleField: graphene.Float,
    peewee.FixedCharField: graphene.String,
    peewee.FloatField: graphene.Float,
    peewee.IntegerField: graphene.Int,
    peewee.PrimaryKeyField: graphene.ID,
    peewee.TextField: graphene.String,
    # TODO support peewee.TimeField
    peewee.UUIDField: graphene.UUID,
}


class PeeweeMapper:
    """
    A mapper for peewee.Model subclasses.
    """

    @staticmethod
    def get_name(model):
        return model.__name__

    @staticmethod
    def get_fields(model):
        fields = {}
        for peewee_field_name, peewee_field in model._meta.fields.items():
            graphene_field = _map_peewee_field(peewee_field)
            if graphene_field is not None:
                fields[peewee_field_name] = graphene_field
        return fields

    @staticmethod
    def get_self_resolver(model):
        """
        Returns a resolver function that resolves a single instance of the model itself.
        """
        def self_resolver(source, info, **kwargs):
            return model.get(*_kwargs_to_peewee_exprs(model, kwargs))
        return self_resolver

    @staticmethod
    def get_self_many_resolver(model):
        """
        Returns a resolver function that resolves many instances of the model itself.
        """
        def self_many_resolver(source, info, **kwargs):
            return model.select().where(*_kwargs_to_peewee_exprs(model, kwargs))
        return self_many_resolver

    @staticmethod
    def get_resolvers(model):
        # For most fields, we can just rely on the underlying Peewee model for resolution.
        # However, we do need custom resolvers for foreign keys
        resolvers = {}
        for field_name, field in model._meta.fields.items():
            if isinstance(field, peewee.ForeignKeyField):
                # TODO cache this and below instances of graphqlize to avoid repeating work
                graphqlized = graphqlize(field.rel_model, mapper=PeeweeMapper)
                resolvers['resolve_{}'.format(field.name)] = graphqlized.resolve
            # TODO support List[ForeignKeyField]
        return resolvers


def _kwargs_to_peewee_exprs(model, kwargs):
    # type: (Any, dict) -> List[peewee.Expression]
    exprs = []
    for field_name, query_value in kwargs.items():
        field = getattr(model, field_name)  # type: Optional[peewee.Field]
        if not field:
            raise GraphQLizeException('Model {} has no field {}'.format(model, field_name))
        exprs.append(field == query_value)
    return exprs


def _map_peewee_field(field):
    """
    Maps a Peewee field to a Graphene field.
    :param field: A peewee.Field subclass.
    :returns: A Graphene field.
    """
    if isinstance(field, peewee.ForeignKeyField):
        return graphene.Field(graphqlize(field.rel_model, mapper=PeeweeMapper), **_map_field_args(field.rel_model))
    # TODO handle one-to-many relationships here somehow? E.g. if ModelA references ModelB many-to-one, ModelB should end up with a List[ModelANode]
    graphene_field = peewee_to_graphene_fields.get(type(field), None)
    if graphene_field:
        return graphene_field(description=field.help_text,
                              default_value=field.default)
    logger.warning('Unable to resolve field %s to a Graphene field', field.name)


def _map_field_args(model):
    args = {}
    for field_name, field in model._meta.fields.items():
        # For now, don't support foreign key fields as arguments. In the future it would
        # be interesting to be able to pass e.g. an id value as an argument to be able
        # to select on foreign key values
        if isinstance(field, peewee.ForeignKeyField):
            continue
        args[field_name] = _map_peewee_field(field)
    return args
