#!/bin/bash

psql -v ON_ERROR_STOP=1 <<-EOSQL
    CREATE ROLE $DB_REPL_USER WITH LOGIN REPLICATION PASSWORD '$DB_REPL_PASSWORD';

    CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';
    CREATE DATABASE $DB_DATABASE OWNER $DB_USER;
EOSQL
