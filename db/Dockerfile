FROM postgres:17.0

RUN mkdir /oracle/pg_data/archive -p && chown -R postgres:postgres /oracle

USER postgres

COPY ./init.sh /docker-entrypoint-initdb.d/init.sh

EXPOSE 22

CMD [ \
    "postgres", \
    "-c", "wal_level=replica", \
    "-c", "wal_log_hints=on", \
    "-c", "max_wal_senders=10", \
    "-c", "archive_mode=on", \
    "-c", "archive_command=cp %p /oracle/pg_data/archive/%f", \
    "-c", "logging_collector=on", \
    "-c", "log_directory=/var/log/postgresql", \
    "-c", "log_filename=postgresql.log", \
    "-c", "log_replication_commands=on" \
]
