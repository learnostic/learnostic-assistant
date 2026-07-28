# Allowlisted tables + columns, given to Claude as context and enforced by
# sql_guardrails.py. This is the access boundary at the prompt level, backed
# by the DB-level GRANT the read-only user already has on these tables.
# Table/schema names are per-tenant (see app/db.py) — reference bare table
# names here, not schema-qualified ones.
#
# Deliberately excluded: students.secret, students.otp, students.otp_expires_at,
# students.otp_attempts, students.login_name — these are authentication
# internals, not student data, and have no legitimate use in a Q&A assistant.
# Also excluded: UI-only styling fields, opaque JSON blobs, and internal
# scheduling plumbing that isn't meaningful to answer staff questions with.
# Review and trim further to match your privacy policy (e.g. address/phone
# fields below are demographic contact info, not auth secrets, but you may
# want to restrict them further).

ALLOWED_TABLES: dict[str, list[str]] = {
    "students": [
        "id", "first_name", "last_name", "email", "phone_number", "dob",
        "gender_id", "nationality_id", "curriculum_id", "school_grade_id",
        "enrolled_grade_id", "enrolled_at", "school", "status",
        "source_of_inquiry", "admin_notes", "created_at", "updated_at",
        "deleted_at",
    ],
    "follow_ups": [
        "id", "student_id", "details", "status", "callback_date",
        "created_at", "updated_at", "location_id", "user_id", "action_date",
        "assessment_id",
    ],
    "students_assesments": [
        "id", "template_id", "student_id", "curriculum_id", "grade_id",
        "subject_id", "title", "predicted_completing_time", "start_time",
        "finish_time", "max_attemps", "attemps", "passmark", "grade_by",
        "created_at", "updated_at", "deleted_at", "results", "comments",
    ],
    "academic_comments": [
        "id", "parent_id", "student_id", "subject_id", "commenter_id",
        "comment", "published_at", "created_at", "updated_at",
        "assessment_id", "lesson_and_events_id",
    ],
    "workbooks": [
        "id", "student_id", "curriculum_id", "grade_id", "subject_id",
        "topic_id", "sub_topic_id", "lesson_id", "taught_by", "attempted_at",
        "status", "attempts", "passed", "created_at", "updated_at",
        "deleted_at",
    ],
    "lesson_and_events": [
        "id", "title", "description", "duration", "branch_id", "tutor_id",
        "service_id", "created_at", "updated_at", "student_id", "status",
        "start", "end", "type", "rated", "studentComment", "studentRate",
    ],
}


# These "status" columns are plain integers in the DB, not enums/strings —
# MySQL silently coerces an unrecognized string comparison (e.g.
# `status = 'pending'`) to 0 rather than erroring, so a wrong guess here
# doesn't fail, it just silently returns the wrong count. Codes pulled from
# the actual backend model classes (app/Models/*.php), not guessed.
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

    status_lines = []
    for column, codes in STATUS_CODES.items():
        mapping = ", ".join(f"{code}={label}" for code, label in codes.items())
        status_lines.append(f"- {column}: {mapping}")

    return (
        "Tables:\n"
        + "\n".join(table_lines)
        + "\n\nStatus code meanings (these columns are integers — always "
        "compare using the number, never the word, e.g. status = 1 not "
        "status = 'active'):\n"
        + "\n".join(status_lines)
    )
