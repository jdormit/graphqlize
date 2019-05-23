from __future__ import absolute_import

import graphene
import peewee
import unittest

from graphqlize import graphqlize, PeeweeMapper


class Widget(peewee.Model):
    id = peewee.PrimaryKeyField()
    size = peewee.IntegerField()
    color = peewee.CharField(help_text='The widget color')


class TestPeeweeMapper(unittest.TestCase):
    def test_get_fields(self):
        graphene_node = graphqlize(Widget, mapper=PeeweeMapper)
        self.assertIsInstance(graphene_node.id, graphene.ID)
        self.assertIsInstance(graphene_node.size, graphene.Int)
        self.assertIsInstance(graphene_node.color, graphene.String)
        self.assertIsNone(graphene_node.size.kwargs['description'])
        self.assertEqual(graphene_node.color.kwargs['description'],
                         'The widget color')
