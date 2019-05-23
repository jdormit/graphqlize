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
    def get_self_resolver(model):
        """
        Returns a resolver function that resolves a single instance of the model itself.
        """
        def self_resolver(*args, **kwargs):
            # TODO instead of this, dynamically generate a query via model.getattr(field_name) == field_value
            return model.get(*args, **kwargs)
        return self_resolver

    @staticmethod
    def get_self_many_resolver(model):
        """
        Returns a resolver function that resolves many instances of the model itself.
        """
        def self_many_resolver(**kwargs):
            return model.select().where
        return self_many_resolver

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
        # TODO ensure that this generated field has proper arguments added to it (to select on the different columns of the referenced model)
        return graphqlize(field.rel_model, mapper=PeeweeMapper)
    # TODO handle one-to-many relationships here somehow? E.g. if ModelA references ModelB many-to-one, ModelB should end up with a List[ModelANode]
    graphene_field = peewee_to_graphene_fields.get(type(field), None)
    if graphene_field:
        # TODO should I add any inputs here?
        return graphene_field(description=field.help_text,
                              default_value=field.default)
    logger.warning('Unable to resolve field %s to a Graphene field',
                   field.name)

