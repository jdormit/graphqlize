from __future__ import absolute_import

import os
import sqlite3
from collections import OrderedDict

import graphene
import peewee
import unittest

from graphqlize import graphqlize, PeeweeMapper


db = peewee.SqliteDatabase('test.db')


class Component(peewee.Model):
    class Meta:
        database = db

    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


class FactoryMachine(peewee.Model):
    class Meta:
        database = db

    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


class Widget(peewee.Model):
    class Meta:
        database = db

    id = peewee.PrimaryKeyField()
    size = peewee.IntegerField()
    color = peewee.CharField(help_text='The widget color')
    constructed_with = peewee.ForeignKeyField(FactoryMachine)


class TestPeeweeMapper(unittest.TestCase):
    def setUp(self):
        try:
            os.remove('test.db')
        except OSError:
            pass
        connection = sqlite3.connect('test.db')
        connection.execute('''
            CREATE TABLE factorymachine (
                id INTEGER PRIMARY KEY,
                name TEXT
            );
        ''')
        connection.execute('''
            CREATE TABLE widget (
                id INTEGER PRIMARY KEY,
                size INTEGER,
                color TEXT,
                constructed_with_id INTEGER,
                FOREIGN KEY (constructed_with_id) REFERENCES factorymachine(id)
            );
        ''')

    def test_get_fields(self):
        graphene_node = graphqlize(Widget, mapper=PeeweeMapper)
        self.assertIsInstance(graphene_node.id, graphene.ID)
        self.assertIsInstance(graphene_node.size, graphene.Int)
        self.assertIsInstance(graphene_node.color, graphene.String)
        self.assertIsInstance(graphene_node.constructed_with, graphene.Field)
        self.assertEqual(graphene_node.constructed_with._type._meta.name, 'FactoryMachine')
        self.assertIsNone(graphene_node.size.kwargs['description'])
        self.assertEqual(graphene_node.color.kwargs['description'],
                         'The widget color')

    def test_get_resolvers(self):
        machine = FactoryMachine.create(name='Green Machine')
        widget = Widget.create(size=3, color='green', constructed_with=machine)

        graphene_node = graphqlize(Widget, mapper=PeeweeMapper)

        class Query(graphene.ObjectType):
            widget = graphene_node.as_field()

        schema = graphene.Schema(query=Query)
        query = """
        query {{
            widget(id: {}) {{
                size
                color
                constructedWith {{
                    id
                    name
                }}
            }}
        }}
        """.format(widget.id)
        result = schema.execute(query)
        expected = OrderedDict([
            ('widget', OrderedDict([
                ('size', 3),
                ('color', u'green'),
                ('constructedWith', OrderedDict([
                    ('id', str(machine.id)),
                    ('name', u'Green Machine'),
                ]))
            ]))
        ])
        self.assertEqual(expected, result.data)
