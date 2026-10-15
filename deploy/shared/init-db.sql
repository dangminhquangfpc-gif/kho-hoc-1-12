-- psql reads this secret inside the DB container; it is not embedded in SQL or arguments.
\set app_password `cat /run/secrets/app_password`
CREATE ROLE tuhoc_app LOGIN PASSWORD :'app_password';
REVOKE ALL ON SCHEMA public FROM PUBLIC;
