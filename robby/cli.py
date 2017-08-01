# -*- coding: utf-8 -*-
import sys
from urlparse import urlparse
import importlib

import click


class UrlType(click.ParamType):
    name = 'uri'

    def convert(self, value, param, ctx):
        try:
            url = urlparse(value)
        except (AttributeError, TypeError):
            self.fail('Invalid url: %s.' % (value,), param, ctx)

        if not url.hostname:
            self.fail('Missing Redis hostname.')

        try:
            int(url.path[1:])
        except (IndexError, ValueError):
            self.fail('Invalid Redis db index.')

        return url


class CallableType(click.ParamType):
    name = 'callable'
    def convert(self, value, param, ctx):
        try:
            mod_name, func_name = value.rsplit('.',1)
            mod = importlib.import_module(mod_name)
            return getattr(mod, func_name)
        except ImportError:
            self.fail('Not a valid callable')


@click.command()
@click.option('--redis-uri', default='redis://localhost:6379/1',
              help='The redis://hostname:port/db to connect to.',
              type=UrlType())
@click.option('--interface', default='localhost',
              help='The interface to bind to.',
              type=str)
@click.option('--port', default=8000,
              help='The TCP port to listen on.',
              type=int)
@click.option('--prefix', default='bayes:',
              help='The Redis keyspace prefix to use.',
              type=str)
@click.option('--logfile',
              help='Where to log output to.',
              type=click.File('a'),
              default=sys.stdout)
@click.option('--stemming/--no-stemming',
              help='Whether or not to use stemming.',
              default=False)
@click.option('--stemming-language',
              help='What language to use for stemming.',
              type=str, default='english')
@click.option('--debug/--no-debug', default=False,
              help='Log debug output or not.')
@click.option('--tokenizer',
              help='Which tokenizer to user', type=CallableType())
def main(redis_uri, interface, port, prefix, logfile, stemming,
         stemming_language, debug, tokenizer):
    from robby.main import Robby
    from twisted.internet import reactor
    from twisted.python import log
    from txredisapi import Connection

    log.startLogging(logfile)

    d = Connection(redis_uri.hostname, int(redis_uri.port or 6379),
                   int(redis_uri.path[1:]))
    d.addCallback(lambda redis: Robby(redis, prefix=prefix, debug=debug,
                                      stemming=stemming,
                                      stemming_language=stemming_language,
                                      tokenizer=tokenizer))
    d.addErrback(log.err)
    d.addCallback(lambda robby: robby.app.run(interface, port))

    reactor.run()
