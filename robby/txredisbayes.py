import math

from twisted.internet import reactor
from twisted.internet.defer import gatherResults, inlineCallbacks, returnValue

from .utils import english_tokenizer, occurances


class TxRedisBayesException(Exception):
    pass


class TxRedisBayes(object):
    """
    A port of https://github.com/jart/redisbayes/ to Twisted

    :param txredis.Redis redis:
        The txredis connection
    """

    clock = reactor

    def __init__(self, redis, prefix="bayes:", correction=0.1,
                 tokenizer=None):
        self.redis = redis
        self.prefix = prefix
        self.correction = correction
        self.tokenizer = tokenizer or english_tokenizer

    def key(self, *parts):
        return '%s%s' % (self.prefix, ':'.join(parts))

    def flush(self):
        d = self.redis.smembers(self.key('categories'))
        d.addCallback(lambda categories: gatherResults([
            self.redis.delete(self.prefix + cat) for cat in categories
        ]))
        d.addCallback(lambda _: self.redis.delete(self.key('categories')))
        return d

    def train(self, category, text):
        d = self.redis.sadd(self.key('categories'), category)
        d.addCallback(lambda _: gatherResults([
            self.redis.hincrby(self.key(category), word, count)
            for word, count in occurances(self.tokenizer(text)).iteritems()
        ]))
        return d

    def untrain(self, category, text):
        word_counts = occurances(self.tokenizer(text)).iteritems()

        @inlineCallbacks
        def untrain_word(word, count):
            cur = yield self.redis.hget(self.key(category), word)
            if not cur:
                return
            new = int(cur) - count
            if new:
                yield self.redis.hset(self.key(category), word, new)
            else:
                yield self.redis.hdel(self.key(category), word)

        def cleanup(category):
            d = self.tally(category)
            d.addCallback(lambda total: gatherResults([
                self.redis.delete(self.key(category)),
                self.redis.srem(self.key('categories'), category),
            ]) if total == 0 else None)
            return d

        d = gatherResults([
            untrain_word(word, count) for word, count in word_counts
        ])
        d.addCallback(lambda _: cleanup(category))
        return d

    def classify(self, text):
        d = self.score(text)
        d.addCallback(
            lambda score: (
                sorted(score.iteritems(), key=lambda v: v[1])[-1][0]
                if score else None))
        return d

    @inlineCallbacks
    def score(self, text):
        occurs = occurances(self.tokenizer(text))
        scores = {}
        categories = yield self.redis.smembers(self.key('categories'))
        for category in categories:
            tally = yield self.tally(category)
            if tally == 0:
                continue
            scores[category] = 0.0
            for word, count in occurs.iteritems():
                score = yield self.redis.hget(self.key(category), word)
                assert not score or score > 0, "corrupt bayesian database"
                score = score or self.correction
                scores[category] += math.log(float(score) / tally)
        returnValue(scores)

    def tally(self, category):
        def raise_(exception):
            raise TxRedisBayesException(exception)

        d = self.redis.hvals(self.key(category))
        d.addCallback(lambda values: sum(int(x) for x in values))
        d.addCallback(
            lambda total: (total if total >= 0
                           else raise_("corrupt bayesian database")))
        return d
