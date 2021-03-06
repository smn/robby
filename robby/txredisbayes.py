import math

import snowballstemmer

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
                 tokenizer=None, stemming=False,
                 stemming_language='english'):
        self.redis = redis
        self.prefix = prefix
        self.correction = correction
        self.tokenizer = tokenizer or english_tokenizer
        self.stemming = stemming
        if self.stemming:
            self.stemmer = snowballstemmer.stemmer(stemming_language)

    def key(self, bucket, *parts):
        return '%s%s@%s' % (self.prefix, bucket, ':'.join(parts))

    def stem_word(self, word):
        if self.stemming:
            return self.stemmer.stemWord(word)
        return word

    def stem_words(self, words):
        if self.stemming:
            return self.stemmer.stemWords(words)
        return words

    def flush(self, bucket='default'):
        d = self.redis.smembers(self.key(bucket, 'categories'))
        d.addCallback(lambda categories: gatherResults([
            self.redis.delete(self.key(bucket, cat)) for cat in categories
        ]))
        d.addCallback(lambda _: self.redis.delete(self.key(bucket, 'categories')))
        return d

    def train(self, category, text, bucket='default'):
        d = self.redis.sadd(self.key(bucket, 'categories'), category)
        d.addCallback(lambda _: gatherResults([
            self.redis.hincrby(self.key(bucket, category), self.stem_word(word), count)
            for word, count in occurances(self.tokenizer(text)).iteritems()
        ]))
        return d

    def untrain(self, category, text, bucket='default'):
        word_counts = occurances(self.tokenizer(text)).iteritems()

        @inlineCallbacks
        def untrain_word(word, count):
            cur = yield self.redis.hget(self.key(bucket, category), word)
            if not cur:
                return
            new = int(cur) - count
            if new:
                yield self.redis.hset(self.key(bucket, category), word, new)
            else:
                yield self.redis.hdel(self.key(bucket, category), word)

        def cleanup(category):
            d = self.tally(category, bucket=bucket)
            d.addCallback(lambda total: gatherResults([
                self.redis.delete(self.key(bucket, category)),
                self.redis.srem(self.key(bucket, 'categories'), category),
            ]) if total == 0 else None)
            return d

        d = gatherResults([
            untrain_word(self.stem_word(word), count)
            for word, count in word_counts
        ])
        d.addCallback(lambda _: cleanup(category))
        return d

    def classify(self, text, bucket='default'):
        d = self.score(text, bucket=bucket)
        d.addCallback(
            lambda score: (
                sorted(score.iteritems(), key=lambda v: v[1])[-1][0]
                if score else None))
        return d

    @inlineCallbacks
    def score(self, text, bucket='default'):
        occurs = occurances(self.stem_words(self.tokenizer(text)))
        scores = {}
        categories = yield self.redis.smembers(self.key(bucket, 'categories'))

        @inlineCallbacks
        def score_category(category):
            tally = yield self.tally(category, bucket=bucket)
            if tally == 0:
                return
            results = yield gatherResults([
                score_word(word, tally, category)
                for word, _ in occurs.iteritems()
            ])
            returnValue((category, sum(results)))

        @inlineCallbacks
        def score_word(word, tally, category):
            score = yield self.redis.hget(self.key(bucket, category), word)
            assert not score or score > 0, "corrupt bayesian database"
            score = score or self.correction
            returnValue(math.log(float(score) / tally))

        scores = yield gatherResults([
            score_category(category)
            for category in categories
        ])
        returnValue(dict(scores))

    def tally(self, category, bucket='default'):
        def raise_(exception):
            raise TxRedisBayesException(exception)

        d = self.redis.hvals(self.key(bucket, category))
        d.addCallback(lambda values: sum(int(x) for x in values))
        d.addCallback(
            lambda total: (total if total >= 0
                           else raise_("corrupt bayesian database")))
        return d
