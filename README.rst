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

Running:

::
    robby \
        --redis-uri redis://127.0.0.1:6379/1 \
        --interface 0.0.0.0 \
        --port 8080 \
        --prefix robby \
        --stemming \
        --stemming-language=english \
        --tokenizer=robby.utils.english_tokenizer \
        --debug


API:

To train it::

    $ curl -d 'training sample' http://localhost:8000/train/category

To untrain it::

    $ curl -d 'training sample' http://localhost:8000/untrain/category

To train it in batches::

    $ curl -d '[{"category": "category", "content": "training sample"}]' http://localhost:8000/batch/train

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
