-- DEV ONLY - Brute Force recreate DB for live dev and unit test
select pg_terminate_backend(pid) from pg_stat_activity where usename = 'tdrive_user';
DROP DATABASE IF EXISTS tdrive_db;
DROP USER IF EXISTS tdrive_user;

-- DEV ONLY - for quick iteration
CREATE USER tdrive_user PASSWORD 'tdrivepass';
CREATE DATABASE tdrive_db owner tdrive_user ENCODING = 'UTF-8';