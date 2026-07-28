# Full schema (all 89 tables), given to Claude as context and enforced by
# sql_guardrails.py. This is the access boundary at the prompt level, backed
# by the DB-level GRANT the read-only user has on these tables.
# Table/schema names are per-tenant (see app/db.py) — reference bare table
# names here, not schema-qualified ones.
#
# Generated from the real backend's schema dump
# (mpa-app/database/schemas/tenant/schema.dump), patched with columns added
# by later migrations not yet squashed into that dump (students.username/
# otp*/admin_notes/source_of_inquiry/show_package_balance,
# lesson_and_events.resourceId/textColor/color/rated/studentRate/
# studentComment/has_attachments/show_package_balance_warning/type — all
# confirmed against the actual migration files, not guessed).
#
# Deliberately excluded even though "include everything" was chosen —
# auth secrets and HR-sensitive data with no legitimate Q&A use case:
#   users: password, remember_token
#   personal_access_tokens: token
#   employees: secret, login_name, national_id_number, passport_number,
#              salary, salary_account
#   students: secret, otp, otp_expires_at, otp_attempts, login_name

ALLOWED_TABLES: dict[str, list[str]] = {
    "academic_comments": ["id", "parent_id", "student_id", "subject_id", "commenter_id", "comment", "published_at", "created_at", "updated_at", "assessment_id", "lesson_and_events_id"],
    "assesment_templates": ["id", "name", "description", "instructions", "curriculum_id", "grade_id", "subject_id", "status", "branch_id", "difficulty", "auto_gradable", "created_at", "updated_at", "deleted_at", "legacy_data"],
    "assesment_templates_activity_log": ["id", "template_id", "user_id", "action", "created_at"],
    "assesment_templates_questions": ["template_id", "question_id"],
    "assesments_backlogs": ["students_assessment_id", "question_id", "attempts", "student_answer", "opened_at", "answered_at", "is_graded", "is_correct", "created_at", "updated_at", "legacy_data"],
    "assessment_event_subjects": ["id", "assessment_event_id", "subject_id", "created_at", "updated_at"],
    "assessment_events": ["id", "title", "student_id", "location_id", "description", "comment", "start", "end", "status", "created_at", "updated_at", "follow_up_id"],
    "attendees": ["id", "event_id", "student_id", "employee_id", "status", "created_at", "updated_at", "internal_note", "shared_note", "invoice_id", "package_balance_status", "reminder_sent"],
    "branches": ["id", "name", "country_id", "address_line_one", "address_line_two", "city", "state_region_province", "zip", "email", "email_verified_at", "previously_verified_email", "phone_number", "published", "settings", "hours", "created_at", "updated_at", "deleted_at"],
    "comments": ["id", "comment_by", "comment", "commentable_id", "commentable_type", "parent_comment", "created_at", "updated_at"],
    "config_values": ["id", "config_id", "value", "code", "selected", "created_at", "updated_at"],
    "configs": ["id", "module_id", "title", "description", "key", "type", "created_at", "updated_at"],
    "countries": ["id", "iso2", "iso3", "name", "native", "phonecode", "currency", "currency_symbol", "region", "subregion", "emoji", "emojiU", "active"],
    "credit_note_numbers": ["id", "location_id", "last_number", "created_at", "updated_at"],
    "curriculum_sub_topics_lookup": ["id", "sub_topic_id", "topic_id", "subject_id", "grade_id", "curriculum_id", "precedence", "published"],
    "curriculum_topics_lookup": ["id", "topic_id", "subject_id", "grade_id", "curriculum_id", "precedence", "curriculums_grades_id"],
    "curriculum_tree": ["id", "digest", "curriculum_id", "grade_id", "subject_id", "topic_id", "subtopic_id", "precedence", "published"],
    "curriculums": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "curriculums_grades": ["id", "curriculum_id", "grade_id", "precedence"],
    "customer_balances": ["id", "customer_id", "balance", "net_payment", "net_invoice", "created_at", "updated_at", "net_credit"],
    "customer_transactions": ["id", "customer_id", "invoice_id", "payment_id", "payment_allocation_id", "amount", "type", "record", "record_type", "created_at", "updated_at"],
    "difficulty": ["id", "name", "level", "published", "created_at", "updated_at", "deleted_at"],
    "email_templates": ["id", "name", "subject", "message", "created_at", "updated_at"],
    "employee_attachment_types": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "employee_next_of_kin": ["id", "employee_id", "relationship_id", "first_name", "last_name", "phone_number", "email", "address_country_id", "address_state", "address_city", "address_zip", "address_line1", "address_line2", "address_phone_number", "created_at", "updated_at", "deleted_at"],
    "employee_payments": ["id", "employee_id", "date_of_payment", "amount", "description", "payslip", "created_at", "updated_at"],
    "employees": ["id", "first_name", "last_name", "email", "phone_number", "dob", "gender_id", "nationality_id", "languages", "address_country_id", "address_state", "address_city", "address_zip", "address_line1", "address_line2", "address_phone_number", "joined", "contract_start", "contract_length", "employee_number", "employment_type_id", "work_shift_id", "work_week", "status", "colour", "settings", "additional_information", "created_at", "updated_at", "deleted_at", "legacy_data"],
    "employees_branches": ["branch_id", "employee_id", "default"],
    "employees_curriculums": ["employee_id", "curriculum_id"],
    "employees_employment_types": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "employees_grades": ["employee_id", "grade_id"],
    "employees_job_designations": ["employee_id", "job_designation_id"],
    "employees_subjects": ["employee_id", "subject_id"],
    "employees_work_shifts": ["id", "name", "start", "end", "published", "created_at", "updated_at", "deleted_at"],
    "follow_ups": ["id", "student_id", "details", "status", "callback_date", "created_at", "updated_at", "location_id", "user_id", "action_date", "parent_id", "assessment_id"],
    "genders": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "grades": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "grades_subjects": ["id", "subject_id", "grade_id", "curriculum_id", "curriculums_grades_id"],
    "invoice_items": ["id", "invoice_id", "type", "value", "description", "unit_price", "quantity", "discount", "total", "created_at", "updated_at"],
    "invoice_numbers": ["id", "last_number", "created_at", "updated_at", "starting_number", "location_id"],
    "invoices": ["id", "customer_id", "start_date", "end_date", "invoice_number", "tax_rate", "tax_treatment", "tax", "sub_total", "total", "reference", "instruction", "status", "created_at", "updated_at", "type", "outstanding", "total_paid", "location_id", "total_package_balance", "deleted_at", "last_sent", "old_invoice_id", "old_invoice_number"],
    "job_designations": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "lesson_activity_logs": ["id", "lesson_id", "employee_id", "action", "created_at"],
    "lesson_and_events": ["id", "title", "description", "duration", "branch_id", "tutor_id", "service_id", "created_at", "updated_at", "show_on_calendar", "show_as_grey", "repeat_id", "student_id", "status", "start", "end", "internal_note", "shared_note", "package_balance_status", "reminder_sent", "invoice_id", "unique_id", "note_sent", "note_sent_at", "resourceId", "textColor", "color", "rated", "studentRate", "studentComment", "has_attachments", "show_package_balance_warning", "type"],
    "lessons": ["id", "title", "branch_id", "topic_id", "subject_id", "sub_topic_id", "grade_id", "curriculum_id", "body", "published", "precedence", "created_at", "updated_at", "deleted_at", "legacy_data"],
    "lessons_additional_reading": ["id", "lesson_id", "href", "description"],
    "lessons_curriculum_paths": ["id", "lesson_id", "published"],
    "media": ["id", "model_type", "model_id", "uuid", "collection_name", "name", "file_name", "mime_type", "disk", "conversions_disk", "size", "manipulations", "custom_properties", "generated_conversions", "responsive_images", "order_column", "created_at", "updated_at"],
    "migrations": ["id", "migration", "batch"],
    "model_has_permissions": ["permission_id", "model_type", "model_id"],
    "model_has_roles": ["role_id", "model_type", "model_id"],
    "modules": ["id", "name", "key", "created_at", "updated_at"],
    "notification_groups": ["id", "key", "title", "created_at", "updated_at"],
    "notification_logs": ["id", "recipient", "subject", "message", "type", "status", "sent_at", "created_at", "updated_at", "sender_email", "log", "recipient_name"],
    "notification_tags": ["id", "tag", "description", "created_at", "updated_at"],
    "notification_template_tags": ["id", "template_id", "tag_id", "created_at", "updated_at"],
    "notification_templates": ["id", "group_id", "title", "key", "subject", "message", "created_at", "updated_at"],
    "package_balances": ["id", "service_id", "customer_id", "purchased", "scheduled", "used", "balance", "created_at", "updated_at", "last_invoice_id"],
    "parents": ["id", "first_name", "last_name", "email", "email_verified", "phone_number", "address_country_id", "address_state", "address_zip", "address_city", "address_line1", "address_line2", "address_phone_number", "created_at", "updated_at", "deleted_at"],
    "payment_allocations": ["id", "invoice_id", "payment_id", "amount", "created_at", "updated_at"],
    "payment_collections": ["id", "customer_id", "amount", "balance", "date", "description", "method", "created_at", "updated_at", "payment_for", "deleted_at", "old_payment_id", "branch_id"],
    "payment_histories": ["id", "invoice_id", "amount", "date", "description", "method", "created_at", "updated_at", "allocation_id"],
    "payment_methods": ["id", "method", "name", "created_at", "updated_at"],
    "permissions": ["id", "name", "guard_name", "description", "assignable", "created_at", "updated_at"],
    "person_relationship_types": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "personal_access_tokens": ["id", "tokenable_type", "tokenable_id", "name", "abilities", "last_used_at", "created_at", "updated_at"],
    "question_activity_logs": ["id", "question_id", "employee_id", "action", "created_at"],
    "question_types": ["id", "name", "label", "description", "published", "created_at", "updated_at", "deleted_at"],
    "questions": ["id", "parent_id", "title", "branch_id", "type_id", "topic_id", "subject_id", "subtopic_id", "grade_id", "curriculum_id", "difficulty_id", "difficulty", "instructions_essay", "body", "answer", "explanation", "hint", "image_src", "published", "guided_practice", "created_at", "updated_at", "deleted_at", "data", "legacy_data"],
    "questions_answers": ["id", "question_id", "type", "value", "explanation", "image_src", "is_correct"],
    "questions_curriculum_paths": ["id", "question_id", "published"],
    "repeat_groups": ["id", "type", "start_date", "end_date", "frequency", "occurrence", "end_type", "created_at", "updated_at"],
    "role_has_permissions": ["permission_id", "role_id"],
    "roles": ["id", "name", "guard_name", "description", "assignable", "created_at", "updated_at", "editable", "label"],
    "services": ["id", "title", "cost", "created_at", "updated_at", "archived", "subject_id", "calendar_color"],
    "student_attachment_types": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "students": ["id", "first_name", "last_name", "email", "email_verified", "phone_number", "dob", "gender_id", "nationality_id", "curriculum_id", "school_grade_id", "enrolled_grade_id", "enrolled_at", "school", "status", "colour", "address_country_id", "address_state", "address_zip", "address_city", "address_line1", "address_line2", "address_phone_number", "additional_information", "created_at", "updated_at", "deleted_at", "data", "legacy_data", "send_lesson_reminder", "username", "email_verified_at", "previously_verified_email", "otp", "otp_expires_at", "otp_attempts", "admin_notes", "source_of_inquiry", "show_package_balance"],
    "students_assesments": ["id", "template_id", "student_id", "curriculum_id", "grade_id", "subject_id", "title", "instructions", "predicted_completing_time", "start_time", "finish_time", "max_attemps", "attemps", "passmark", "grade_by", "created_at", "updated_at", "deleted_at", "results", "comments", "legacy_data"],
    "students_branches": ["branch_id", "student_id", "default"],
    "students_parents": ["student_id", "parent_id", "relationship_id"],
    "students_subjects": ["student_id", "subject_id", "last_attended", "last_feedback"],
    "sub_topics": ["id", "name", "topic_id", "precedence", "published", "created_at", "updated_at", "deleted_at"],
    "subjects": ["id", "name", "published", "created_at", "updated_at", "deleted_at"],
    "topics": ["id", "name", "subject_id", "precedence", "published", "created_at", "updated_at", "deleted_at"],
    "un_availabilities": ["id", "employee_id", "description", "start_date", "start_time", "end_date", "end_time", "created_at", "updated_at", "repeat_id"],
    "users": ["id", "type", "type_id", "login_id", "status", "created_at", "updated_at", "deleted_at", "branches"],
    "workbooks": ["id", "student_id", "curriculum_id", "grade_id", "subject_id", "topic_id", "sub_topic_id", "lesson_id", "taught_by", "attempted_at", "status", "attempts", "passed", "previous", "next", "created_at", "updated_at", "deleted_at", "results", "provisional_results"],
    "workbooks_lessons": ["workbook_id", "lesson_id", "order"],
    "workbooks_questions": ["workbook_id", "question_id", "attempts", "opened_at", "answered_at", "student_answer", "is_graded", "is_correct"],
}

# Foreign key relationships, for JOIN guidance. Format: "table.column -> ref_table.ref_column"
TABLE_RELATIONSHIPS: dict[str, list[str]] = {
    "academic_comments": ["academic_comments.parent_id -> academic_comments.id", "academic_comments.student_id -> students.id", "academic_comments.subject_id -> subjects.id"],
    "assesment_templates": ["assesment_templates.branch_id -> branches.id", "assesment_templates.curriculum_id -> curriculums.id", "assesment_templates.grade_id -> grades.id", "assesment_templates.subject_id -> subjects.id"],
    "assesment_templates_activity_log": ["assesment_templates_activity_log.template_id -> assesment_templates.id", "assesment_templates_activity_log.user_id -> users.id"],
    "assesment_templates_questions": ["assesment_templates_questions.question_id -> questions.id", "assesment_templates_questions.template_id -> assesment_templates.id"],
    "assesments_backlogs": ["assesments_backlogs.question_id -> questions.id", "assesments_backlogs.students_assessment_id -> students_assesments.id"],
    "assessment_event_subjects": ["assessment_event_subjects.subject_id -> subjects.id"],
    "assessment_events": ["assessment_events.location_id -> branches.id", "assessment_events.student_id -> students.id"],
    "attendees": ["attendees.invoice_id -> invoices.id"],
    "branches": ["branches.country_id -> countries.id"],
    "comments": ["comments.parent_comment -> comments.id"],
    "config_values": ["config_values.config_id -> configs.id"],
    "configs": ["configs.module_id -> modules.id"],
    "curriculum_sub_topics_lookup": ["curriculum_sub_topics_lookup.curriculum_id -> curriculums.id", "curriculum_sub_topics_lookup.grade_id -> grades.id", "curriculum_sub_topics_lookup.sub_topic_id -> sub_topics.id", "curriculum_sub_topics_lookup.subject_id -> subjects.id", "curriculum_sub_topics_lookup.topic_id -> topics.id"],
    "curriculum_topics_lookup": ["curriculum_topics_lookup.curriculum_id -> curriculums.id", "curriculum_topics_lookup.curriculums_grades_id -> curriculums_grades.id", "curriculum_topics_lookup.grade_id -> grades.id", "curriculum_topics_lookup.subject_id -> subjects.id", "curriculum_topics_lookup.topic_id -> topics.id"],
    "curriculum_tree": ["curriculum_tree.curriculum_id -> curriculums.id", "curriculum_tree.grade_id -> grades.id", "curriculum_tree.subject_id -> subjects.id", "curriculum_tree.subtopic_id -> sub_topics.id", "curriculum_tree.topic_id -> topics.id"],
    "curriculums_grades": ["curriculums_grades.curriculum_id -> curriculums.id", "curriculums_grades.grade_id -> grades.id"],
    "customer_balances": ["customer_balances.customer_id -> students.id"],
    "employee_next_of_kin": ["employee_next_of_kin.employee_id -> employees.id", "employee_next_of_kin.relationship_id -> person_relationship_types.id"],
    "employees": ["employees.employment_type_id -> employees_employment_types.id", "employees.work_shift_id -> employees_work_shifts.id", "employees.address_country_id -> countries.id", "employees.gender_id -> genders.id", "employees.nationality_id -> countries.id"],
    "employees_branches": ["employees_branches.branch_id -> branches.id", "employees_branches.employee_id -> employees.id"],
    "employees_curriculums": ["employees_curriculums.curriculum_id -> curriculums.id", "employees_curriculums.employee_id -> employees.id"],
    "employees_grades": ["employees_grades.employee_id -> employees.id", "employees_grades.grade_id -> grades.id"],
    "employees_job_designations": ["employees_job_designations.job_designation_id -> job_designations.id", "employees_job_designations.employee_id -> employees.id"],
    "employees_subjects": ["employees_subjects.employee_id -> employees.id", "employees_subjects.subject_id -> subjects.id"],
    "grades_subjects": ["grades_subjects.curriculum_id -> curriculums.id", "grades_subjects.curriculums_grades_id -> curriculums_grades.id", "grades_subjects.grade_id -> grades.id", "grades_subjects.subject_id -> subjects.id"],
    "invoices": ["invoices.customer_id -> students.id", "invoices.location_id -> branches.id"],
    "lesson_activity_logs": ["lesson_activity_logs.employee_id -> employees.id", "lesson_activity_logs.lesson_id -> lessons.id"],
    "lesson_and_events": ["lesson_and_events.branch_id -> branches.id", "lesson_and_events.invoice_id -> invoices.id", "lesson_and_events.repeat_id -> repeat_groups.id", "lesson_and_events.service_id -> services.id", "lesson_and_events.tutor_id -> employees.id"],
    "lessons": ["lessons.branch_id -> branches.id", "lessons.curriculum_id -> curriculums.id", "lessons.grade_id -> grades.id", "lessons.sub_topic_id -> sub_topics.id", "lessons.subject_id -> subjects.id", "lessons.topic_id -> topics.id"],
    "lessons_additional_reading": ["lessons_additional_reading.lesson_id -> lessons.id"],
    "lessons_curriculum_paths": ["lessons_curriculum_paths.lesson_id -> lessons.id"],
    "model_has_permissions": ["model_has_permissions.permission_id -> permissions.id"],
    "model_has_roles": ["model_has_roles.role_id -> roles.id"],
    "package_balances": ["package_balances.customer_id -> students.id", "package_balances.last_invoice_id -> invoices.id", "package_balances.service_id -> services.id"],
    "parents": ["parents.address_country_id -> countries.id"],
    "payment_allocations": ["payment_allocations.invoice_id -> invoices.id", "payment_allocations.payment_id -> payment_collections.id"],
    "payment_collections": ["payment_collections.customer_id -> students.id"],
    "payment_histories": ["payment_histories.allocation_id -> payment_allocations.id"],
    "question_activity_logs": ["question_activity_logs.employee_id -> employees.id", "question_activity_logs.question_id -> questions.id"],
    "questions": ["questions.branch_id -> branches.id", "questions.curriculum_id -> curriculums.id", "questions.difficulty_id -> difficulty.id", "questions.grade_id -> grades.id", "questions.parent_id -> questions.id", "questions.subject_id -> subjects.id", "questions.subtopic_id -> sub_topics.id", "questions.topic_id -> topics.id", "questions.type_id -> question_types.id"],
    "questions_answers": ["questions_answers.question_id -> questions.id"],
    "questions_curriculum_paths": ["questions_curriculum_paths.question_id -> questions.id"],
    "role_has_permissions": ["role_has_permissions.permission_id -> permissions.id", "role_has_permissions.role_id -> roles.id"],
    "students": ["students.address_country_id -> countries.id", "students.curriculum_id -> curriculums.id", "students.enrolled_grade_id -> grades.id", "students.gender_id -> genders.id", "students.nationality_id -> countries.id", "students.school_grade_id -> grades.id"],
    "students_assesments": ["students_assesments.curriculum_id -> curriculums.id", "students_assesments.grade_id -> grades.id", "students_assesments.student_id -> students.id", "students_assesments.subject_id -> subjects.id", "students_assesments.template_id -> assesment_templates.id"],
    "students_branches": ["students_branches.branch_id -> branches.id", "students_branches.student_id -> students.id"],
    "students_parents": ["students_parents.parent_id -> parents.id", "students_parents.relationship_id -> person_relationship_types.id", "students_parents.student_id -> students.id"],
    "students_subjects": ["students_subjects.student_id -> students.id", "students_subjects.subject_id -> subjects.id"],
    "sub_topics": ["sub_topics.topic_id -> topics.id"],
    "topics": ["topics.subject_id -> subjects.id"],
    "un_availabilities": ["un_availabilities.employee_id -> employees.id", "un_availabilities.repeat_id -> repeat_groups.id"],
    "workbooks": ["workbooks.curriculum_id -> curriculums.id", "workbooks.grade_id -> grades.id", "workbooks.lesson_id -> lessons.id", "workbooks.student_id -> students.id", "workbooks.sub_topic_id -> sub_topics.id", "workbooks.subject_id -> subjects.id", "workbooks.topic_id -> topics.id"],
    "workbooks_lessons": ["workbooks_lessons.lesson_id -> lessons.id", "workbooks_lessons.workbook_id -> workbooks.id"],
    "workbooks_questions": ["workbooks_questions.question_id -> questions.id", "workbooks_questions.workbook_id -> workbooks.id"],
}

# These "status" columns are plain integers in the DB, not enums/strings —
# MySQL silently coerces an unrecognized string comparison (e.g.
# `status = 'pending'`) to 0 rather than erroring, so a wrong guess here
# doesn't fail, it just silently returns the wrong count. Codes pulled from
# the actual backend model classes (app/Models/*.php), not guessed. Only
# 3 of the many status-like columns are confirmed here — see the general
# "undocumented codes" rule in the SQL prompt for the rest.
STATUS_CODES: dict[str, dict[int, str]] = {
    "students.status": {0: "Inactive", 1: "Active", 2: "Prospective", 3: "Pause"},
    "follow_ups.status": {
        0: "Open", 1: "Callback", 2: "Assessment", 3: "Converted",
        4: "Dead end", 5: "Assessment Report", 6: "In Renewal",
        7: "Renewed", 8: "Scheduled", 9: "Other",
    },
    "lesson_and_events.status": {
        0: "Scheduled", 1: "Cancelled", 2: "Attended", 3: "Missed",
        5: "Unavailable",
    },
}


def render_schema_context() -> str:
    if not ALLOWED_TABLES:
        raise RuntimeError(
            "ALLOWED_TABLES is empty — fill in app/schema_context.py with the "
            "real Learnostic table/column names before serving requests."
        )
    table_lines = [f"- {table}({', '.join(columns)})" for table, columns in ALLOWED_TABLES.items()]

    relationship_lines = []
    for rels in TABLE_RELATIONSHIPS.values():
        relationship_lines.extend(rels)

    status_lines = []
    for column, codes in STATUS_CODES.items():
        mapping = ", ".join(f"{code}={label}" for code, label in codes.items())
        status_lines.append(f"- {column}: {mapping}")

    return (
        "Tables:\n"
        + "\n".join(table_lines)
        + "\n\nForeign key relationships (use these for JOINs — do not guess "
        "a join column that isn't listed here):\n"
        + "\n".join(relationship_lines)
        + "\n\nStatus code meanings (these columns are integers — always "
        "compare using the number, never the word, e.g. status = 1 not "
        "status = 'active'):\n"
        + "\n".join(status_lines)
    )
