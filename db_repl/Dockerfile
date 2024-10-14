FROM postgres:17.0

COPY ./docker-entrypoint-dbrepl.sh /
USER postgres

CMD ["/docker-entrypoint-dbrepl.sh"]
