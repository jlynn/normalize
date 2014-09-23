#
# This file is a part of the normalize python library
#
# normalize is free software: you can redistribute it and/or modify
# it under the terms of the MIT License.
#
# normalize is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# MIT License for more details.
#
# You should have received a copy of the MIT license along with
# normalize.  If not, refer to the upstream repository at
# http://github.com/hearsaycorp/normalize
#

"""tests that look at the wholistic behavior of records"""

from __future__ import absolute_import

from datetime import datetime
import unittest2

from normalize import JsonProperty
from normalize import JsonRecord
from normalize import Property
from normalize import Record
import normalize.exc as exc
from normalize.property.types import DateProperty
from normalize.visitor import VisitorPattern


class TestRecords(unittest2.TestCase):
    """Test that the new data descriptor classes work"""

    def test_false_emptiness(self):
        """Test that Properties with falsy empty values don't throw exceptions"""

        class SophiesRecord(Record):
            placeholder = Property()
            aux_placeholder = Property(empty='')
            age = Property(empty=0)
            name = Property(empty=None)

        sophie = SophiesRecord()
        with self.assertRaises(AttributeError):
            sophie.placeholder

        self.assertEqual(sophie.aux_placeholder, '')
        self.assertEqual(sophie.age, 0)
        self.assertEqual(sophie.name, None)

        # the properties aren't really set...
        self.assertEqual(VisitorPattern.visit(sophie), {})

        sophie.age = 1
        self.assertEqual(VisitorPattern.visit(sophie), {"age": 1})

        # setting a property to the empty value is the same as deleting it,
        # even if the value passes the type constraint.
        sophie.age = 0
        self.assertEqual(VisitorPattern.visit(sophie), {})

    def test_json_emptiness(self):
        """JSON is ambiguous.  Deal with it."""

        class SophiesJsonRecord(JsonRecord):
            placeholder = JsonProperty()
            aux_placeholder = JsonProperty(empty='')
            age = JsonProperty(empty=0)
            name = JsonProperty(empty=Exception)

        sophie = SophiesJsonRecord({})
        self.assertEqual(sophie.placeholder, None)
        self.assertEqual(sophie.aux_placeholder, '')
        self.assertEqual(sophie.age, 0)

        with self.assertRaises(AttributeError):
            sophie.name

        self.assertEqual(sophie.json_data(), {})

    def test_functional_emptiness(self):
        """Test that functional empty values are transient"""

        class BlahRecord(Record):
            blah = Property(empty=None)

        class LambdaRecord(Record):
            epoch = Property(empty=lambda: datetime(1970, 1, 1, 0, 0, 0))
            objective = Property(empty=BlahRecord)

        lambda_ = LambdaRecord()

        self.assertTrue(
            lambda_.epoch.isoformat().startswith("1970-01-01T00:00:00"),
            "lambda empty values are called",
        )

        lambda_.objective.blah = "blah"
        self.assertEqual(lambda_.objective.blah, None,
                         "functions as empty values don't persist")

    def test_exceptional_emptiness(self):

        class ExplosiveRecord(Record):
            bio = Property(empty=ValueError('fooo bar'))
            about = Property(empty=IOError)

        boom = ExplosiveRecord()

        with self.assertRaises(IOError):
            boom.about

        with self.assertRaises(ValueError):
            boom.bio

    def test_bad_empty_constructors(self):

        class DatedRecord(Record):
            some_date_field = DateProperty(json_name="hello")

        dated = DatedRecord()
        self.assertEqual(getattr(dated, "some_date_field", "bob"), "bob")
