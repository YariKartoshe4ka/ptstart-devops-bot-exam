#!/bin/bash

rm -rf /var/lib/postgresql/*/main/data/*

while :; do
    for i in {1..5}; do
        PGPASSWORD="$DB_REPL_PASSWORD" \
            pg_basebackup -R -h "$DB_HOST" -U "$DB_REPL_USER" -D /var/lib/postgresql/*/main/data && break 2

        echo 'Waiting for master to connect...'
        sleep 2s
    done

    echo 'Failed to connect to master'
    exit 2
done

echo 'Backup done, starting replica...'
