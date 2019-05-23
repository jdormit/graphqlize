"""
Mapping logic for Peewee models
"""
import logging
import peewee
import graphene

from graphqlize import graphqlize

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
    # TODO resolve peewee.ForeignKeyFields to graphqlized nodes
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
    def get_resolvers(model):
        # TODO implement me
        return {}


def _map_peewee_field(field):
    """
    Maps a Peewee field to a Graphene field.
    :param field: A peewee.Field subclass.
    :returns: A Graphene field.
    """
    if isinstance(field, peewee.ForeignKeyField):
        return graphqlize(field.rel_model, mapper=PeeweeMapper)
    graphene_field = peewee_to_graphene_fields.get(type(field), None)
    if graphene_field:
        return graphene_field(description=field.help_text,
                              default_value=field.default)
    logger.warning('Unable to resolve field %s to a Graphene field',
                   field.name)

