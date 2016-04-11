FROM praekeltfoundation/python-base

COPY . /robby
RUN pip install -e /robby

ENTRYPOINT ["eval-args.sh", "dinit", "/robby/robby-entrypoint.sh"]
