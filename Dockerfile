FROM praekeltfoundation/python-base

RUN apt-get-install.sh gcc
COPY . /robby
RUN pip install -e /robby
RUN apt-get-purge.sh gcc

ENTRYPOINT ["eval-args.sh", "dinit", "/robby/robby-entrypoint.sh"]
