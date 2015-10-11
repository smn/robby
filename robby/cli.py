# -*- coding: utf-8 -*-
import sys
from urlparse import urlparse

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
@click.option('--debug/--no-debug', default=False,
              help='Log debug output or not.')
def main(redis_uri, interface, port, prefix, logfile, debug):
    from robby.main import Robby
    from twisted.internet import reactor
    from twisted.python import log
    from txredisapi import Connection

    log.startLogging(logfile)

    d = Connection(redis_uri.hostname, int(redis_uri.port or 6379))
    d.addCallback(lambda redis: Robby(redis, prefix=prefix, debug=debug))
    d.addCallback(lambda robby: robby.app.run(interface, port))

    reactor.run()
