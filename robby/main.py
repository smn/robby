import json

from klein import Klein

from twisted.internet import reactor
from twisted.internet.defer import gatherResults
from twisted.web import server

from .txredisbayes import TxRedisBayes


class RobbySite(server.Site):

    debug = False

    def log(self, request):
        if self.debug:
            server.Site.log(self, request)


class Robby(object):
    """
    Robby, Probability as a Service.
    A simple REST based API for Naive Bayesian Inference.

    :param txredisapi.Connection redis:
        The txredis connection
    """

    app = Klein()
    clock = reactor
    timeout = 5

    def __init__(self, redis, prefix="bayes:", correction=0.1,
                 tokenizer=None, debug=False, stemming=False,
                 stemming_language='english'):
        self.redis = redis
        self.debug = debug
        self.bayes = TxRedisBayes(self.redis,
                                  prefix=prefix,
                                  correction=correction,
                                  tokenizer=tokenizer,
                                  stemming=stemming,
                                  stemming_language=stemming_language)

    @app.route('/train/<category>')
    def train(self, request, category):
        request.setHeader('Content-Type', 'application/json')
        d = self.bayes.train(category, request.content.read())
        d.addCallback(lambda result: json.dumps(result))
        return d

    @app.route('/batch/train')
    def batch_train(self, request):
        request.setHeader('Content-Type', 'application/json')
        data = json.load(request.content)

        d = gatherResults([
            self.bayes.train(item['category'], item['content'])
            for item in data])
        d.addCallback(lambda result: json.dumps(result))
        return d

    @app.route('/untrain/<category>')
    def untrain(self, request, category):
        request.setHeader('Content-Type', 'application/json')
        d = self.bayes.untrain(category, request.content.read())
        d.addCallback(lambda result: json.dumps(result))
        return d

    @app.route('/classify')
    def classify(self, request):
        request.setHeader('Content-Type', 'application/json')
        d = self.bayes.classify(request.content.read())
        d.addCallback(lambda result: json.dumps({
            'category': result,
        }))
        return d

    @app.route('/score')
    def score(self, request):
        request.setHeader('Content-Type', 'application/json')
        d = self.bayes.score(request.content.read())
        d.addCallback(lambda result: json.dumps(result))
        return d

    @app.route('/flush')
    def flush(self, request):
        request.setHeader('Content-Type', 'application/json')
        d = self.bayes.flush()
        d.addCallback(lambda result: json.dumps(result))
        return d
