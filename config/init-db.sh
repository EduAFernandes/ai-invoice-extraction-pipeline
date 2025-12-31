#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE invoice_db;
    CREATE USER invoice_user WITH PASSWORD 'secure_password';
    GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;
EOSQL

echo "Created invoice_db database and invoice_user"
