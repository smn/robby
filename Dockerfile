FROM praekeltfoundation/python-base:2.7

WORKDIR /app

COPY . /app
RUN pip install -e .

ENTRYPOINT ["tini", "--", "/app/robby-entrypoint.sh"]
CMD []
