FROM praekeltfoundation/python-base

RUN apt-get-install.sh python-dev
COPY . /robby
RUN pip install -e /robby

ENTRYPOINT ["eval-args.sh", "dinit", "/robby/robby-entrypoint.sh"]
