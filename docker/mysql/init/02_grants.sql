-- Creates the read-only app user and grants SELECT on all 89 tables the app
-- now has schema context for (see app/schema_context.py). Runs after
-- 01_customer_1_dump.sql (alphabetical order in /docker-entrypoint-initdb.d),
-- which creates customer_1 and its tables from a real (gitignored) dump of
-- the local backend's dev data.
--
-- NOTE: these are table-level grants, not column-level. The handful of
-- columns we exclude (users.password, personal_access_tokens.token,
-- employees.secret/national_id_number/etc., students.secret/otp*) are
-- blocked at the application layer (sql_guardrails.py + the model never
-- seeing them in its schema context), not at the DB layer — this user can
-- still technically SELECT those columns directly via a raw mysql client.
-- Column-level GRANTs for just those ~4 tables would close that gap if
-- wanted later.
--
-- NOTE: 01_customer_1_dump.sql is NOT checked into git (multi-GB, contains
-- base64 images) — pull it fresh from mpa-db before `docker compose up` on
-- a new machine. Without that file, this script alone creates the user but
-- there is no customer_1 database yet for it to have access to.

CREATE USER IF NOT EXISTS 'learnostic_readonly'@'%' IDENTIFIED BY 'devpassword';

GRANT SELECT ON customer_1.academic_comments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assesment_templates TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assesment_templates_activity_log TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assesment_templates_questions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assesments_backlogs TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assessment_event_subjects TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.assessment_events TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.attendees TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.branches TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.comments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.config_values TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.configs TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.countries TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.credit_note_numbers TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.curriculum_sub_topics_lookup TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.curriculum_topics_lookup TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.curriculum_tree TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.curriculums TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.curriculums_grades TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.customer_balances TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.customer_transactions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.difficulty TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.email_templates TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employee_attachment_types TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employee_next_of_kin TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employee_payments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_branches TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_curriculums TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_employment_types TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_grades TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_job_designations TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_subjects TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.employees_work_shifts TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.follow_ups TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.genders TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.grades TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.grades_subjects TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.invoice_items TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.invoice_numbers TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.invoices TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.job_designations TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lesson_activity_logs TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lesson_and_events TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lessons TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lessons_additional_reading TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.lessons_curriculum_paths TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.media TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.migrations TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.model_has_permissions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.model_has_roles TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.modules TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.notification_groups TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.notification_logs TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.notification_tags TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.notification_template_tags TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.notification_templates TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.package_balances TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.parents TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.payment_allocations TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.payment_collections TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.payment_histories TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.payment_methods TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.permissions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.person_relationship_types TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.personal_access_tokens TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.question_activity_logs TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.question_types TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.questions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.questions_answers TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.questions_curriculum_paths TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.repeat_groups TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.role_has_permissions TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.roles TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.services TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.student_attachment_types TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students_assesments TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students_branches TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students_parents TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.students_subjects TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.sub_topics TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.subjects TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.topics TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.un_availabilities TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.users TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.workbooks TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.workbooks_lessons TO 'learnostic_readonly'@'%';
GRANT SELECT ON customer_1.workbooks_questions TO 'learnostic_readonly'@'%';

FLUSH PRIVILEGES;
