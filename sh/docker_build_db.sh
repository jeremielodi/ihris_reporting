#!/bin/bash

# bash script mode
# set -o pipefail


echo "[build]"
echo "Building Database"

set -a
source .env
set +a


# Set the password in the PGPASSWORD environment variable
export PGPASSWORD=$DB_PASSWORD
# create database ihris_test with owner ima2;
docker cp db postgres_server:/
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/clear-db.sql $DB_NAME
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/schema.sql $DB_NAME
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/functions.sql $DB_NAME
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/config.sql $DB_NAME
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/data/countries.sql $DB_NAME
docker exec -it postgres_server psql -h 127.0.0.1 -U $DB_USER  -f ./db/data/default.sql $DB_NAME

#PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -f ./db/function.sql  $DB_NAME

# psql -h 127.0.0.1 -U postgres -f ./db/migrations/08.sql data_collect
# psql -h 127.0.0.1 -U postgres -f ./db/data/loop.sql data_collect
# pm2 start server/app.js --node-args="--max-old-space-size=1024"

# psql -h 127.0.0.1 -U postgres -f ./data_collect6.sql data_collect

# psql -h 127.0.0.1 -U postgres -d data_collect

#pg_dump  -h 127.0.0.1 -U postgres data_collect > ~/data_collect6.sql
