from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

import txredisapi

from robby.txredisbayes import TxRedisBayes

from .samples import SAMPLE_TEXT_1, SAMPLE_TEXT_2


class TxRedisBayesTest(TestCase):

    timeout = 1

    @inlineCallbacks
    def setUp(self):
        self.redis = yield txredisapi.Connection()
        self.bayes = TxRedisBayes(self.redis)

    def tearDown(self):
        d = self.bayes.flush()
        d.addCallback(lambda _: self.redis.disconnect())
        return d

    def category_exists(self, category):
        return self.redis.sismember(self.bayes.key('categories'), category)

    def add_category(self, category):
        return self.redis.sadd(self.bayes.key('categories'), category)

    def incr_word_count(self, category, word, count):
        return self.redis.hincrby(self.bayes.key(category), word, count)

    def get_word_count(self, category, word):
        return self.redis.hget(self.bayes.key(category), word)

    @inlineCallbacks
    def test_flush(self):
        yield self.add_category('testing')
        yield self.incr_word_count('testing', 'foo', 1)
        self.assertTrue((yield self.category_exists('testing')))
        self.assertEqual((yield self.get_word_count('testing', 'foo')), 1)
        yield self.bayes.flush()
        self.assertFalse((yield self.category_exists('testing')))
        self.assertFalse((yield self.get_word_count('testing', 'foo')))

    @inlineCallbacks
    def test_train(self):
        self.assertFalse((yield self.category_exists('testing')))
        self.assertFalse((yield self.get_word_count('testing', 'lorem')))
        yield self.bayes.train('testing', SAMPLE_TEXT_1)
        self.assertTrue((yield self.category_exists('testing')))
        self.assertEqual(
            (yield self.get_word_count('testing', 'lorem')), 1)

    @inlineCallbacks
    def test_untrain(self):
        yield self.bayes.train('testing', 'lorem')
        yield self.bayes.untrain('testing', 'lorem')
        self.assertEqual(
            (yield self.get_word_count('testing', 'lorem')), None)
        self.assertFalse(
            (yield self.category_exists('testing')))

    @inlineCallbacks
    def test_classify(self):
        yield self.bayes.train('lorem', SAMPLE_TEXT_1)
        yield self.bayes.train('monty', SAMPLE_TEXT_2)
        self.assertEqual((yield self.bayes.classify(SAMPLE_TEXT_1)),
                         'lorem')
        self.assertEqual((yield self.bayes.classify(SAMPLE_TEXT_2)),
                         'monty')
