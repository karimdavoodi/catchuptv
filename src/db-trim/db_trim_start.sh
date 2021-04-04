#!/bin/bash


su postgres sh -c "/usr/lib/postgresql/12/bin/postgres -D /data -c config_file=/etc/postgresql/12/main/postgresql.conf" &
sleep 5

echo "SELECT 'CREATE DATABASE trim' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'trim')\gexec" | psql -U postgres

/postgrest /etc/postgrest.conf  
