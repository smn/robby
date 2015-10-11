#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
import txredisapi

from robby.main import Robby


class TestRobby(TestCase):

    @inlineCallbacks
    def setUp(self):
        self.redis = yield txredisapi.Connection()
        self.robby = Robby(self.redis)

    def tearDown(self):
        return self.redis.disconnect()

    def test_000_something(self):
        pass
