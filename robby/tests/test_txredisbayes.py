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
        d = self.bayes.flush("bucket")
        d.addCallback(lambda _: self.redis.disconnect())
        return d

    def category_exists(self, bucket, category):
        return self.redis.sismember(
            self.bayes.key(bucket, 'categories'), category)

    def add_category(self, bucket, category):
        return self.redis.sadd(
            self.bayes.key(bucket, 'categories'), category)

    def incr_word_count(self, bucket, category, word, count):
        return self.redis.hincrby(
            self.bayes.key(bucket, category), word, count)

    def get_word_count(self, bucket, category, word):
        return self.redis.hget(self.bayes.key(bucket, category), word)

    @inlineCallbacks
    def test_flush(self):
        yield self.add_category('bucket', 'testing')
        yield self.incr_word_count('bucket', 'testing', 'foo', 1)
        self.assertTrue((yield self.category_exists('bucket', 'testing')))
        self.assertEqual(
            (yield self.get_word_count('bucket', 'testing', 'foo')), 1)
        yield self.bayes.flush('bucket')
        self.assertFalse((yield self.category_exists('bucket', 'testing')))
        self.assertFalse(
            (yield self.get_word_count('bucket', 'testing', 'foo')))

    @inlineCallbacks
    def test_train(self):
        self.assertFalse((yield self.category_exists('bucket', 'testing')))
        self.assertFalse(
            (yield self.get_word_count('bucket', 'testing', 'lorem')))
        yield self.bayes.train('testing', SAMPLE_TEXT_1, bucket='bucket')
        self.assertTrue((yield self.category_exists('bucket', 'testing')))
        self.assertEqual(
            (yield self.get_word_count('bucket', 'testing', 'lorem')), 1)

    @inlineCallbacks
    def test_untrain(self):
        yield self.bayes.train('testing', 'lorem', bucket='bucket')
        yield self.bayes.untrain('testing', 'lorem', bucket='bucket')
        self.assertEqual(
            (yield self.get_word_count('bucket', 'testing', 'lorem')), None)
        self.assertFalse(
            (yield self.category_exists('bucket', 'testing')))

    @inlineCallbacks
    def test_classify(self):
        yield self.bayes.train('lorem', SAMPLE_TEXT_1, bucket='bucket')
        yield self.bayes.train('monty', SAMPLE_TEXT_2, bucket='bucket')
        self.assertEqual((yield self.bayes.classify(SAMPLE_TEXT_1, bucket='bucket')),
                         'lorem')
        self.assertEqual((yield self.bayes.classify(SAMPLE_TEXT_2, bucket='bucket')),
                         'monty', )
