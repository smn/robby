from klein import Klein

from twisted.internet import reactor
from twisted.web import server


class RobbySite(server.Site):

    debug = False

    def log(self, request):
        if self.debug:
            server.Site.log(self, request)


class Robby(object):
    """
    Robby, Probability as a Service.
    A simple REST based API for Naive Bayesian Inference.

    :param txredis.Redis redis:
        The txredis connection
    """

    app = Klein()
    debug = False
    clock = reactor
    timeout = 5

    def __init__(self, redis):
        self.redis = redis
