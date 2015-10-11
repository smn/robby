from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

import txredisapi

from robby.txredisbayes import TxRedisBayes

SAMPLE_TEXT_1 = """
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex
ea commodo consequat. Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.""".strip()

SAMPLE_TEXT_2 = """
Guard:  Halt!  Who goes there?
Arthur: It is I, Arthur, son of Uther Pendragon, from the castle of Camelot.
        King of the Britons, defeater of the Saxons, sovereign of all England!
Guard:  Who's the other one?
Arthur: I am, and this is my trusty servant Patsy.  We have ridden the
        and breadth of the land in search of knights who will join me in my
        court at Camelot.  I must speak with your lord and master.
Guard:  What, ridden on a horse?
Arthur: Yes.
Guard:  You're using coconuts!
Arthur: What?""".strip()


class TxRedisBayesTest(TestCase):

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
