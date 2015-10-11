#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.web.client import HTTPConnectionPool
from twisted.web.server import Site

import txredisapi

import treq

from robby.main import Robby

from .samples import SAMPLE_TEXT_1, SAMPLE_TEXT_2


class TestRobby(TestCase):

    @inlineCallbacks
    def setUp(self):
        self.redis = yield txredisapi.Connection()
        self.addCleanup(self.redis.disconnect)
        self.robby = Robby(self.redis)
        self.addCleanup(self.robby.bayes.flush)

        self.site = Site(self.robby.app.resource())
        self.listener = reactor.listenTCP(0, self.site, interface='localhost')
        self.listener_port = self.listener.getHost().port
        self.addCleanup(self.listener.loseConnection)

        # cleanup stuff for treq's global http request pool
        self.pool = HTTPConnectionPool(reactor, persistent=False)
        self.addCleanup(self.pool.closeCachedConnections)

    def request(self, method, path, data=None):
        return treq.request(
            method, 'http://localhost:%s%s' % (
                self.listener_port,
                path
            ),
            data=data,
            pool=self.pool)

    @inlineCallbacks
    def test_classify(self):
        yield self.robby.bayes.train('sample1', SAMPLE_TEXT_1)
        yield self.robby.bayes.train('sample2', SAMPLE_TEXT_2)
        response = yield self.request('PUT', '/classify', data=SAMPLE_TEXT_1)
        data = yield response.json()
        self.assertEqual(data, {
            'category': 'sample1'
        })

    @inlineCallbacks
    def test_train(self):
        yield self.request('PUT', '/train/sample1', data=SAMPLE_TEXT_1)
        yield self.request('PUT', '/train/sample2', data=SAMPLE_TEXT_2)
        response = yield self.request('PUT', '/classify', data=SAMPLE_TEXT_1)
        data = yield response.json()
        self.assertEqual(data, {
            'category': 'sample1'
        })

    @inlineCallbacks
    def test_untrain(self):
        yield self.request('PUT', '/train/sample1', data=SAMPLE_TEXT_1)
        yield self.request('PUT', '/untrain/sample1', data=SAMPLE_TEXT_1)
        response = yield self.request('PUT', '/classify', data=SAMPLE_TEXT_1)
        data = yield response.json()
        self.assertEqual(data, {
            'category': None
        })

    @inlineCallbacks
    def test_score(self):
        yield self.request('PUT', '/train/sample1', data=SAMPLE_TEXT_1)
        response = yield self.request('PUT', '/score', data=SAMPLE_TEXT_1)
        data = yield response.json()
        self.assertEqual(int(data['sample1']), -211)

    @inlineCallbacks
    def test_flush(self):
        yield self.request('PUT', '/train/sample1', data=SAMPLE_TEXT_1)
        self.assertTrue(
            (yield self.redis.sismember(
                self.robby.bayes.key('categories'), 'sample1')))
        response = yield self.request('POST', '/flush')
        data = yield response.json()
        self.assertEqual(int(data), 1)
        self.assertFalse(
            (yield self.redis.sismember(
                self.robby.bayes.key('categories'), 'sample1')))
