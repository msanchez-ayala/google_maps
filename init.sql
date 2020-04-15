-- Drop, create fresh defaultdb
DROP DATABASE IF EXISTS
  defaultdb;
CREATE DATABASE
  defaultdb;

-- Create superuser
CREATE USER
  google_user
WITH
  SUPERUSER PASSWORD 'passw0rd';

-- Grant privileges
GRANT
  ALL PRIVILEGES
ON
  DATABASE defaultdb
TO google_user;
