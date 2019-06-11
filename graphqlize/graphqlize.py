"""
Top-level GraphQLize module.
"""
import graphene
from typing import Any, Dict, Callable, Type
from typing_extensions import Protocol


class Mapper(Protocol):
    def get_name(self, model):
        # type: (Any) -> str
        pass

    def get_fields(self, model):
        # type: (Any) -> Dict[str, graphene.Field]
        pass

    def get_resolvers(self, model):
        # type: (Any) -> Dict[str, Callable]
        pass

    def get_self_resolver(self, model):
        # type: (Any) -> Callable
        pass

    def get_self_many_resolver(self, model):
        # type: (Any) -> Callable
        pass


def graphqlize(model, mapper):
    # type: (Any, Mapper) -> Type[graphene.ObjectType]
    """
    Returns a new subclass of graphene.ObjectType with fields and
    field resolvers generated from `model`, where `model` is a
    supported model class (e.g., a peewee.Model subclass).

    :param model: The model to graphqlize.
    :param mapper: A mapper object that knows how to generate Graphene fields
                   and resolvers from the model. It should have the methods
                   get_name(model), which returns the name of the GraphQL node,
                   get_fields(model), which returns a dictionary of field name
                   to graphene.Field objects, get_resolvers(model), which
                   returns a dictionary of resolver name to resolver function,
                   get_self_resolver(model), which returns a resolver callable
                   for the model itself, and get_self_many_resolver(model), which
                   returns a resolver callable that resolves a List of the model
                   itself.
    :returns: graphene.ObjectType
    """
    # TODO add mutations - CUD
    name = mapper.get_name(model)
    fields = mapper.get_fields(model)
    resolvers = mapper.get_resolvers(model)
    self_resolver = mapper.get_self_resolver(model)
    self_many_resolver = mapper.get_self_many_resolver(model)
    graphqlized = _graphene_object_type(name, fields, resolvers, self_resolver, self_many_resolver)
    return graphqlized


def _graphene_object_type(name, fields, resolvers, self_resolver, self_many_resolver):
    # type: (str, Dict[str, graphene.Field], Dict[str, Callable], Callable, Callable) -> Type[graphene.ObjectType]
    """
    Returns a new graphene.ObjectType with the given name, fields, and resolvers.
    :param name: The name of the node.
    :param fields: A dictionary mapping field names to graphene.Field objects.
    :param resolvers: A dictionary mapping resolver names to callables.
    :param self_resolver: A callable to be attached to the created model as the resolve to get one of the object.
    :param self_many_resolver: A callable to be attached to the created model as the resolver to get
                               many of the object.
    :return: graphene.ObjectType
    """
    obj_dict = fields.copy()
    obj_dict.update(resolvers)
    obj_dict['resolve'] = self_resolver
    obj_dict['resolve_many'] = self_many_resolver

    argument_fields = fields.copy()
    for field_name, field in fields.items():
        if isinstance(field, graphene.Field):
            # TODO actually support querying on child nodes?
            argument_fields.pop(field_name)
        elif isinstance(field, graphene.List):
            # TODO what to do here?
            argument_fields.pop(field_name)

    def as_field(self):
        return graphene.Field(self, resolver=self_resolver, **argument_fields)
    obj_dict['as_field'] = classmethod(as_field)

    def as_many_field(self):
        return graphene.List(self, resolver=self_many_resolver, **argument_fields)
    obj_dict['as_many_field'] = classmethod(as_many_field)

    return type(name, (graphene.ObjectType,), obj_dict)
