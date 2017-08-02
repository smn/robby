Robby
=====

Probabilities as a Service

.. image:: https://img.shields.io/travis/smn/robby.svg
        :target: https://travis-ci.org/smn/robby

.. image:: https://img.shields.io/pypi/v/robby.svg
        :target: https://pypi.python.org/pypi/robby

.. image:: https://coveralls.io/repos/smn/robby/badge.png?branch=develop
    :target: https://coveralls.io/r/smn/robby?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/robby/badge/?version=latest
    :target: https://robby.readthedocs.org
    :alt: Robby Documentation

Available as a docker container with ``docker pull sdehaan/robby``.
The docker container allow the for the following environment variables:

* REDIS_HOST, defaults to ``127.0.0.1``
* REDIS_PORT, defaults to ``6379``
* REDIS_DB, defaults to ``1``
* ROBBY_PORT, defaults to ``8080``
* ROBBY_PREFIX, the prefix for Redis keys, defaults to ``robby``
* ROBBY_STEMMING_LANGUAGE, defaults to ``english``
* ROBBY_TOKENIZER, the python callable to use for tokenizing. Defaults to ``robby.utils.english_tokenizer``, ``robby.utils.dumb_tokenizer`` is also available.

Or ``pip install robby`` and run directly::

    robby \
        --redis-uri redis://127.0.0.1:6379/1 \
        --interface 0.0.0.0 \
        --port 8080 \
        --prefix robby \
        --stemming \
        --stemming-language=english \
        --tokenizer=robby.utils.english_tokenizer \
        --debug

API
---

To train it::

    $ curl -d 'training sample' http://localhost:8000/train/category

To untrain it::

    $ curl -d 'training sample' http://localhost:8000/untrain/category

To train it in batches::

    $ curl -d '[{"category": "category", "content": "training sample"}]' http://localhost:8000/batch/train

To classify::

    $ curl -d 'sample message' http://localhost:8000/classify
    {
        "category": "category"
    }

To get scoring::

    $ curl -d 'sample message' http://localhost:8000/score
    {
        "category": 0.01
    }

To get clear the db::

    $ curl http://localhost:8000/flush
