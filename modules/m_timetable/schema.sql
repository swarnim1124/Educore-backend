-- =========================================================================
-- Schema Definition for OneApp Timetable Module (m_timetable)
-- Source: MASTER DATA MGMT Excel (SCH_TIMETABLE) & BRS/FRS Specification
-- =========================================================================

CREATE SCHEMA IF NOT EXISTS sch_timetable;


-- 1. Working Day Configuration
-- Defines which days of the week are working days per institution / academic year.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_working_day (
    id              SERIAL PRIMARY KEY,
    inst_id         INT NOT NULL,                           -- FK -> sch_org.tb_inst
    academic_year_id INT,                                   -- FK -> sch_academic_struct.tb_acad_year
    name            VARCHAR(128),                           -- Configuration pattern name (e.g. Normal Week, Exam Week)
    effective_from  DATE,
    effective_to    DATE,
    day_of_week_id  SMALLINT NOT NULL,                      -- FK -> sch_lookup.tb_lookup (MONDAY=1..SUNDAY=7)
    day_name        VARCHAR(20),                            -- MONDAY, TUESDAY, etc.
    is_working_day  BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(inst_id, academic_year_id, day_of_week_id, effective_from)
);


-- 2. Time Slot Configuration
-- Defines the institution-wide period grid (Period 1, Lunch Break, etc.)
CREATE TABLE IF NOT EXISTS sch_timetable.tb_time_slot (
    id              SERIAL PRIMARY KEY,
    inst_id         INT NOT NULL,                           -- FK -> sch_org.tb_inst
    slot_name       VARCHAR(128) NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    slot_sequence   INT NOT NULL,                           -- slotOrder
    is_break        BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(inst_id, slot_name),
    UNIQUE(inst_id, slot_sequence),
    UNIQUE(inst_id, start_time, end_time),
    CHECK(start_time < end_time)
);


-- 3. Timetable Header
-- Represents a complete timetable for a section/term within an effective period.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_tt (
    id              SERIAL PRIMARY KEY,
    inst_id         INT NOT NULL,                           -- FK -> sch_org.tb_inst
    academic_year_id INT,                                   -- FK -> sch_academic_struct.tb_acad_year
    term_id         INT,                                    -- FK -> sch_academic_struct.tb_acad_term
    program_id      INT,                                    -- FK -> sch_academic_struct.tb_program
    semester_id     INT,                                    -- FK -> sch_academic_struct.tb_semester
    sec_id          INT NOT NULL,                           -- FK -> sch_academic_struct.tb_sec
    tt_code         VARCHAR(128) NOT NULL,
    version_no      INT NOT NULL DEFAULT 1,
    effective_from  DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to    DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '1 year'),
    status_id       VARCHAR(50) NOT NULL DEFAULT 'DRAFT',   -- DRAFT, PENDING_APPROVAL, ACTIVE, PUBLISHED, REJECTED, ARCHIVED
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by      INT,
    updated_by      INT,
    UNIQUE(sec_id, tt_code),
    UNIQUE(sec_id, version_no),
    CHECK(effective_from <= effective_to)
);


-- 4. Timetable Entry
-- Individual slots mapping course + section + faculty + room to day/time.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_tt_entry (
    id                      SERIAL PRIMARY KEY,
    tt_id                   INT NOT NULL REFERENCES sch_timetable.tb_tt(id),
    inst_id                 INT,                            -- FK -> sch_org.tb_inst
    academic_year_id        INT,                            -- FK -> sch_academic_struct.tb_acad_year
    term_id                 INT,                            -- FK -> sch_academic_struct.tb_acad_term
    program_id              INT,                            -- FK -> sch_academic_struct.tb_program
    semester_id             INT,                            -- FK -> sch_academic_struct.tb_semester
    sec_id                  INT,                            -- FK -> sch_academic_struct.tb_sec
    course_id               VARCHAR(100),                   -- FK -> sch_curriculum.tb_course
    crs_offering_id         INT,                            -- FK -> sch_course_ops.tb_crs_offering
    fac_id                  INT,                            -- FK -> sch_emp_fac.tb_fac
    fac_crs_assignment_id   INT,                            -- FK -> sch_course_ops.tb_fac_crs_assignment
    working_day_id          INT,                            -- FK -> sch_timetable.tb_working_day
    day_of_week             VARCHAR(20),                    -- MONDAY, TUESDAY, etc.
    time_slot_id            INT NOT NULL REFERENCES sch_timetable.tb_time_slot(id),
    room_id                 INT,                            -- FK -> sch_infra.tb_room
    session_type_id         VARCHAR(50) DEFAULT 'LECTURE',  -- LECTURE, LAB, TUTORIAL, SEMINAR
    start_date              DATE DEFAULT CURRENT_DATE,
    end_date                DATE DEFAULT (CURRENT_DATE + INTERVAL '1 year'),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CHECK(start_date <= end_date)
);


-- 5. Timetable Entry Section Linkage
-- Supports multi-section sharing of a single timetable entry.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_tt_entry_sec (
    id              SERIAL PRIMARY KEY,
    tt_entry_id     INT NOT NULL REFERENCES sch_timetable.tb_tt_entry(id) ON DELETE CASCADE,
    sec_id          INT NOT NULL,                           -- FK -> sch_academic_struct.tb_sec
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tt_entry_id, sec_id)
);


-- 6. Class Session
-- Materialized daily class instances derived from timetable entries.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_class_session (
    id                  SERIAL PRIMARY KEY,
    tt_entry_id         INT NOT NULL REFERENCES sch_timetable.tb_tt_entry(id),
    session_date        DATE NOT NULL,
    session_status_id   VARCHAR(50) NOT NULL DEFAULT 'SCHEDULED',   -- SCHEDULED, COMPLETED, CANCELLED, RESCHEDULED
    session_source_id   VARCHAR(50) NOT NULL DEFAULT 'TT',          -- TT (timetable), EXTRA (extra class)
    remarks             TEXT,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tt_entry_id, session_date)
);


-- 7. Class Session Faculty
-- Tracks which faculty conducts each session (supports substitution and co-teaching).
CREATE TABLE IF NOT EXISTS sch_timetable.tb_class_session_fac (
    id                  SERIAL PRIMARY KEY,
    class_session_id    INT NOT NULL REFERENCES sch_timetable.tb_class_session(id) ON DELETE CASCADE,
    fac_id              INT NOT NULL,                       -- FK -> sch_emp_fac.tb_fac
    is_primary          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_session_id, fac_id)
);


-- 8. Class Session Room
-- Tracks which room is used for each session (supports room overrides).
CREATE TABLE IF NOT EXISTS sch_timetable.tb_class_session_room (
    id                  SERIAL PRIMARY KEY,
    class_session_id    INT NOT NULL REFERENCES sch_timetable.tb_class_session(id) ON DELETE CASCADE,
    room_id             INT NOT NULL,                       -- FK -> sch_infra.tb_room
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_session_id, room_id)
);


-- 9. Class Session Change (Substitution, Reschedule, Room Change)
-- Records any change to a scheduled session.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_class_session_change (
    id                  SERIAL PRIMARY KEY,
    class_session_id    INT REFERENCES sch_timetable.tb_class_session(id),
    tt_entry_id         INT REFERENCES sch_timetable.tb_tt_entry(id),
    change_type_id      VARCHAR(50) NOT NULL DEFAULT 'FAC_CHANGE', -- FAC_CHANGE, ROOM_CHANGE, RESCHEDULE, TIME_CHANGE
    old_fac_id          INT,                                -- FK -> sch_emp_fac.tb_fac
    new_fac_id          INT,                                -- FK -> sch_emp_fac.tb_fac (substituteFacultyId)
    old_room_id         INT,                                -- FK -> sch_infra.tb_room
    new_room_id         INT,                                -- FK -> sch_infra.tb_room
    old_session_date    DATE,
    new_session_date    DATE,
    old_time_slot_id    INT,                                -- FK -> sch_timetable.tb_time_slot
    new_time_slot_id    INT,                                -- FK -> sch_timetable.tb_time_slot
    reason              TEXT NOT NULL,
    status              VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, CANCELLED, EXPIRED
    approved_by         INT,                                -- FK -> sch_iam.tb_user
    approved_on         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by          INT
);


-- 10. Class Cancellation
-- Records class cancellations with reason tracking.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_class_cancellation (
    id                      SERIAL PRIMARY KEY,
    class_session_id        INT NOT NULL UNIQUE REFERENCES sch_timetable.tb_class_session(id),
    cancellation_reason_id  VARCHAR(50) NOT NULL,           -- HOLIDAY, FAC_LEAVE, INSTITUTIONAL, OTHER
    cancelled_by            INT NOT NULL,                   -- FK -> sch_iam.tb_user
    cancelled_on            TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks                 TEXT,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- 11. Extra Class
-- Records additional/makeup classes outside the regular timetable.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_extra_class (
    id                  SERIAL PRIMARY KEY,
    crs_offering_id     INT,                                -- FK -> sch_course_ops.tb_crs_offering
    course_id           VARCHAR(100),                       -- FK -> sch_curriculum.tb_course
    sec_id              INT NOT NULL,                       -- FK -> sch_academic_struct.tb_sec
    fac_id              INT NOT NULL,                       -- FK -> sch_emp_fac.tb_fac
    room_id             INT,                                -- FK -> sch_infra.tb_room
    session_date        DATE NOT NULL,
    time_slot_id        INT NOT NULL REFERENCES sch_timetable.tb_time_slot(id),
    session_type_id     VARCHAR(50) DEFAULT 'EXTRA',        -- EXTRA, MAKEUP, REMEDIAL
    reason              TEXT NOT NULL,
    class_session_id    INT REFERENCES sch_timetable.tb_class_session(id),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by          INT,
    UNIQUE(sec_id, session_date, time_slot_id),
    UNIQUE(fac_id, session_date, time_slot_id),
    UNIQUE(room_id, session_date, time_slot_id)
);


-- 12. Holiday Adjustment
-- Maps holiday working-day shifts within an academic term.
CREATE TABLE IF NOT EXISTS sch_timetable.tb_holiday_adjustment (
    id                      SERIAL PRIMARY KEY,
    acad_term_id            INT NOT NULL,                   -- FK -> sch_academic_struct.tb_acad_term
    holiday_date            DATE NOT NULL,
    adjustment_type_id      VARCHAR(50) NOT NULL,           -- WORKING_DAY_SHIFT, COMPENSATORY, OTHER
    source_working_day_id   INT REFERENCES sch_timetable.tb_working_day(id),
    target_working_day_id   INT REFERENCES sch_timetable.tb_working_day(id),
    target_date             DATE,
    remarks                 TEXT,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by              INT,
    UNIQUE(acad_term_id, holiday_date)
);


-- =========================================================================
-- Indexes for Performance
-- =========================================================================

CREATE INDEX IF NOT EXISTS idx_working_day_inst ON sch_timetable.tb_working_day(inst_id);
CREATE INDEX IF NOT EXISTS idx_working_day_acad_year ON sch_timetable.tb_working_day(academic_year_id);
CREATE INDEX IF NOT EXISTS idx_time_slot_inst ON sch_timetable.tb_time_slot(inst_id);
CREATE INDEX IF NOT EXISTS idx_tt_sec ON sch_timetable.tb_tt(sec_id);
CREATE INDEX IF NOT EXISTS idx_tt_status ON sch_timetable.tb_tt(status_id);
CREATE INDEX IF NOT EXISTS idx_tt_entry_tt ON sch_timetable.tb_tt_entry(tt_id);
CREATE INDEX IF NOT EXISTS idx_tt_entry_room ON sch_timetable.tb_tt_entry(room_id);
CREATE INDEX IF NOT EXISTS idx_tt_entry_fac ON sch_timetable.tb_tt_entry(fac_id);
CREATE INDEX IF NOT EXISTS idx_tt_entry_day_slot ON sch_timetable.tb_tt_entry(day_of_week, time_slot_id);
CREATE INDEX IF NOT EXISTS idx_class_session_date ON sch_timetable.tb_class_session(session_date);
CREATE INDEX IF NOT EXISTS idx_class_session_entry ON sch_timetable.tb_class_session(tt_entry_id);
CREATE INDEX IF NOT EXISTS idx_class_session_fac_fac ON sch_timetable.tb_class_session_fac(fac_id);
CREATE INDEX IF NOT EXISTS idx_class_session_change_session ON sch_timetable.tb_class_session_change(class_session_id);
CREATE INDEX IF NOT EXISTS idx_class_session_change_type ON sch_timetable.tb_class_session_change(change_type_id);
CREATE INDEX IF NOT EXISTS idx_extra_class_date ON sch_timetable.tb_extra_class(session_date);
CREATE INDEX IF NOT EXISTS idx_holiday_adj_term ON sch_timetable.tb_holiday_adjustment(acad_term_id);
