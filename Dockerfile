FROM praekeltfoundation/python-base

RUN apt-get-install.sh gcc python-dev
COPY . /robby
RUN pip install -e /robby
RUN apt-get-purge.sh gcc python-dev

ENTRYPOINT ["eval-args.sh", "dinit", "/robby/robby-entrypoint.sh"]
