"""
Top-level GraphQLize module.
"""


def graphqlize(model):
    """
    Returns a new subclass of graphene.ObjectType with fields and
    field resolvers generated from `model`, where `model` is a
    supported model class (e.g., a peewee.Model subclass).

    :param: model - The model to graphqlize
    :return: graphene.ObjectType
    """
    # get fields for new class
    # get resolvers for new class
    # construct new class via type()
    pass
