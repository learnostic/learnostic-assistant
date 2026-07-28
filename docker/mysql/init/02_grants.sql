-- Creates the read-only app user and grants SELECT on the 6 tables this
-- app is allowed to query. Runs after 01_customer_1_dump.sql (alphabetical
-- order in /docker-entrypoint-initdb.d), which creates customer_1 and its
-- tables from a real (gitignored) dump of the local backend's dev data.
--
-- NOTE: 01_customer_1_dump.sql is NOT checked into git (multi-GB, contains
-- base64 images) — pull it fresh from mpa-db before `docker compose up` on
-- a new machine. Without that file, this script alone creates the user but
-- there is no customer_1 database yet for it to have access to.

CREATE USER IF NOT EXISTS 'learnostic_readonly'@'%' IDENTIFIED BY 'devpassword';

GRANT SELECT ON customer_1.students TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.follow_ups TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students_assesments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.academic_comments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.workbooks TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lesson_and_events TO 'learnostic_readonly'@'%';

FLUSH PRIVILEGES;
