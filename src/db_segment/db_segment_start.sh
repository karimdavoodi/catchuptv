#!/bin/bash

#TODO: MUST set in YAML file
export MQ_HOST='192.168.1.23'
export MQ_USER='karim'
export MQ_PASS='31233123'
export MQ_EXCHANGE='segment_info'
export DB_HOST='localhost'
export DB_DATABASE='segment'
export DB_USER='postgres'
export DB_PASS='31233123'

su postgres sh -c "/usr/lib/postgresql/12/bin/postgres -D /data -c config_file=/etc/postgresql/12/main/postgresql.conf" &
sleep 5

echo "SELECT 'CREATE DATABASE segment' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'segment')\gexec" | psql -U postgres

/postgrest /etc/postgrest.conf & 
python3 /db_epg_insert.py  
