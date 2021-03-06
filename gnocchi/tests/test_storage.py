# -*- encoding: utf-8 -*-
#
# Copyright © 2014 eNovance
#
# Authors: Julien Danjou <julien@danjou.info>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import datetime

import testscenarios

from gnocchi import storage
from gnocchi.storage import null
from gnocchi import tests

load_tests = testscenarios.load_tests_apply_scenarios


class TestStorageDriver(tests.TestCase):
    def test_get_driver(self):
        self.conf.set_override('driver', 'null', 'storage')
        driver = storage.get_driver(self.conf)
        self.assertIsInstance(driver, null.NullStorage)

    def test_create_entity(self):
        self.storage.create_entity("foo", [(1, 1)])

    def test_create_entity_already_exists(self):
        self.storage.create_entity("foo", [(1, 1)])
        self.assertRaises(storage.EntityAlreadyExists,
                          self.storage.create_entity,
                          "foo", [(1, 1)])

    def test_delete_entity(self):
        self.storage.create_entity("foo", [(1, 1)])
        self.storage.delete_entity("foo")

    def test_add_and_get_measures(self):
        self.storage.create_entity("foo", [(5, 3)])
        self.storage.add_measures('foo', [
            storage.Measure(datetime.datetime(2014, 1, 1, 12, 0, 1), 69),
            storage.Measure(datetime.datetime(2014, 1, 1, 12, 7, 31), 42),
            storage.Measure(datetime.datetime(2014, 1, 1, 12, 9, 31), 4),
            storage.Measure(datetime.datetime(2014, 1, 1, 12, 12, 45), 44),
        ])

        values = self.storage.get_measures('foo')
        self.assertEqual(3, len(values))
        self.assertEqual(4, values[datetime.datetime(2014, 1, 1, 12, 9, 30)])
        self.assertEqual(44, values[datetime.datetime(2014, 1, 1, 12, 12, 45)])
        self.assertEqual(42, values[datetime.datetime(2014, 1, 1, 12, 7, 30)])

        values = self.storage.get_measures(
            'foo',
            from_timestamp='2014-01-01 12:10:10')
        self.assertEqual(1, len(values))
        self.assertEqual(44, values[datetime.datetime(2014, 1, 1, 12, 12, 45)])

        values = self.storage.get_measures('foo',
                                           to_timestamp='2014-01-01 12:10:10')
        self.assertEqual(2, len(values))
        self.assertEqual(42, values[datetime.datetime(2014, 1, 1, 12, 7, 30)])
        self.assertEqual(4, values[datetime.datetime(2014, 1, 1, 12, 9, 30)])

        values = self.storage.get_measures(
            'foo',
            to_timestamp='2014-01-01 12:10:10',
            from_timestamp='2014-01-01 12:10:10')
        self.assertEqual({}, values)

        values = self.storage.get_measures(
            'foo',
            to_timestamp='2014-01-01 12:10:10',
            from_timestamp='2014-01-01 12:09:30')
        self.assertEqual(1, len(values))
        self.assertEqual(4, values[datetime.datetime(2014, 1, 1, 12, 9, 30)])

    def test_get_measure_unknown_entity(self):
        self.assertRaises(storage.EntityDoesNotExist,
                          self.storage.get_measures,
                          'foo', 0)
