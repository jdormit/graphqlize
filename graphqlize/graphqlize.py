"""
Top-level GraphQLize module.
"""
import graphene


def graphqlize(model, mapper):
    """
    Returns a new subclass of graphene.ObjectType with fields and
    field resolvers generated from `model`, where `model` is a
    supported model class (e.g., a peewee.Model subclass).

    :param model: The model to graphqlize.
    :param mapper: A mapper object that knows how to generate Graphene fields
                   and resolvers from the model. It should have the methods
                   get_name(model), which returns the name of the GraphQL node,
                   get_fields(model), which returns a dictionary of field name
                   to graphene.Field objects, and get_resolvers(model), which
                   returns a dictionary of resolver name to resolver function.
    :returns: graphene.ObjectType
    """
    name = mapper.get_name(model)
    fields = mapper.get_fields(model)
    resolvers = mapper.get_resolvers(model)
    return graphene_object_type(name, fields, resolvers)


def graphene_object_type(name, fields, resolvers):
    """
    Returns a new graphene.ObjectType with the given name, fields, and resolvers.
    :param name: The name of the node.
    :param fields: A dictionary mapping field names to graphene.Field objects.
    :param resolvers: A dictionary mapping resolver names to callables.
    :return: graphene.ObjectType
    """
    field_dict = fields
    field_dict.update(resolvers)
    return type(name, (graphene.ObjectType,), field_dict)
