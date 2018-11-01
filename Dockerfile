FROM praekeltfoundation/python-base:3.6

# RUN apt-get-install.sh gcc python-dev
WORKDIR /app

COPY . /app
RUN pip install -e .
# RUN apt-get-purge.sh gcc python-dev

ENTRYPOINT ["tini", "--", "/app/robby-entrypoint.sh"]
CMD []
