#!/bin/bash

rm -rf /var/lib/postgresql/data/*

while :; do
    for i in {1..5}; do
        PGPASSWORD="$DB_REPL_PASSWORD" \
            pg_basebackup -R -h "$DB_HOST_MASTER" -U "$DB_REPL_USER" -D /var/lib/postgresql/data && break 2

        echo 'Waiting for master to connect...'
        sleep 2s
    done

    echo 'Failed to connect to master'
    exit 2
done

echo 'Backup done, starting replica...'

chmod 700 /var/lib/postgresql/data
postgres
