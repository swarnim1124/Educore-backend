-- =========================================================================
-- Schema Definition for OneApp Examinations & Results Module (m_exam)
-- =========================================================================

CREATE SCHEMA IF NOT EXISTS sch_exam;

-- 1. Exam Centres
CREATE TABLE IF NOT EXISTS sch_exam.tb_exam_centre (
    id SERIAL PRIMARY KEY,
    inst_id INT NOT NULL,
    centre_name VARCHAR(255) NOT NULL,
    address TEXT,
    capacity INT NOT NULL CHECK (capacity > 0),
    courses JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Exam Schedule & Version History
CREATE TABLE IF NOT EXISTS sch_exam.tb_exam_schedule (
    id SERIAL PRIMARY KEY,
    inst_id INT NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    exam_type VARCHAR(100) DEFAULT 'regular',
    courses JSONB DEFAULT '[]'::jsonb,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    sessions JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'draft',
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_exam_schedule_history (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    status VARCHAR(50) NOT NULL,
    version INT NOT NULL,
    snapshot JSONB NOT NULL,
    reason TEXT,
    changed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Seating Plan
CREATE TABLE IF NOT EXISTS sch_exam.tb_seating_plan (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    venue_id INT NOT NULL REFERENCES sch_exam.tb_exam_centre(id),
    course_id VARCHAR(100) NOT NULL,
    allocation_method VARCHAR(50) DEFAULT 'auto',
    student_ids JSONB DEFAULT '[]'::jsonb,
    seat_mappings JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Invigilator Assignment
CREATE TABLE IF NOT EXISTS sch_exam.tb_invigilator_assignment (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    venue_id INT NOT NULL REFERENCES sch_exam.tb_exam_centre(id),
    faculty_id INT NOT NULL,
    duty_type VARCHAR(100) DEFAULT 'assistant_invigilator',
    status VARCHAR(50) DEFAULT 'assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Student Block & Hall Tickets
CREATE TABLE IF NOT EXISTS sch_exam.tb_student_block (
    id SERIAL PRIMARY KEY,
    stud_id INT NOT NULL,
    schedule_id INT REFERENCES sch_exam.tb_exam_schedule(id),
    reason TEXT NOT NULL,
    blocked_by INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_hall_ticket (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    stud_id INT NOT NULL,
    venue_details TEXT,
    seat_number VARCHAR(50),
    status VARCHAR(50) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_hall_ticket_publication (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    status VARCHAR(50) DEFAULT 'published',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Question Paper & Question Bank
CREATE TABLE IF NOT EXISTS sch_exam.tb_question_paper (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    set_by INT NOT NULL,
    content TEXT NOT NULL,
    difficulty_level VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'draft',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_question_bank (
    id SERIAL PRIMARY KEY,
    paper_id INT NOT NULL REFERENCES sch_exam.tb_question_paper(id),
    tags JSONB DEFAULT '[]'::jsonb,
    category VARCHAR(100),
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. External Examiner & Evaluation
CREATE TABLE IF NOT EXISTS sch_exam.tb_external_examiner (
    id SERIAL PRIMARY KEY,
    inst_id INT NOT NULL,
    examiner_name VARCHAR(255) NOT NULL,
    qualification VARCHAR(255),
    specialization VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    is_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_external_evaluation (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    examiner_id INT NOT NULL REFERENCES sch_exam.tb_external_examiner(id),
    script_bundle_ids JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'dispatched',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Internal Exam (CIE)
CREATE TABLE IF NOT EXISTS sch_exam.tb_internal_exam (
    id SERIAL PRIMARY KEY,
    course_offering_id INT NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    exam_type_id INT DEFAULT 1,
    max_marks NUMERIC(5,2) NOT NULL,
    exam_date DATE,
    components JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_internal_marks (
    id SERIAL PRIMARY KEY,
    exam_id INT NOT NULL REFERENCES sch_exam.tb_internal_exam(id),
    stud_id INT NOT NULL,
    component_id INT DEFAULT 1,
    marks NUMERIC(5,2) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_internal_marks_consolidation (
    id SERIAL PRIMARY KEY,
    course_offering_id INT NOT NULL,
    academic_term_id INT NOT NULL,
    stud_id INT NOT NULL,
    consolidated_score NUMERIC(5,2) NOT NULL,
    override_marks NUMERIC(5,2),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Marks Entry, Verification & Grading
CREATE TABLE IF NOT EXISTS sch_exam.tb_marks_entry (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    examiner_id INT NOT NULL,
    stud_id INT NOT NULL,
    marks NUMERIC(5,2) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INT,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_grade (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    stud_id INT NOT NULL,
    grade VARCHAR(10) NOT NULL,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Evaluation Bundle, Second Valuation & Moderation
CREATE TABLE IF NOT EXISTS sch_exam.tb_evaluation_bundle (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    evaluator_id INT NOT NULL,
    student_ids JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_second_valuation (
    id SERIAL PRIMARY KEY,
    bundle_id INT NOT NULL REFERENCES sch_exam.tb_evaluation_bundle(id),
    stud_id INT NOT NULL,
    second_evaluator_id INT NOT NULL,
    marks NUMERIC(5,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_moderation (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    course_id VARCHAR(100) NOT NULL,
    moderation_rule VARCHAR(255) NOT NULL,
    adjustment NUMERIC(5,2) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Results
CREATE TABLE IF NOT EXISTS sch_exam.tb_result (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    stud_id INT NOT NULL,
    gpa NUMERIC(4,2) NOT NULL,
    cgpa NUMERIC(4,2) NOT NULL,
    result_status VARCHAR(50) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Result Approval & Publication
CREATE TABLE IF NOT EXISTS sch_exam.tb_result_approval (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    level INT NOT NULL,
    approver_role VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_result_publication (
    id SERIAL PRIMARY KEY,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    status VARCHAR(50) DEFAULT 'published',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Revaluation & Appeals
CREATE TABLE IF NOT EXISTS sch_exam.tb_revaluation_request (
    id SERIAL PRIMARY KEY,
    stud_id INT NOT NULL,
    course_id VARCHAR(100) NOT NULL,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sch_exam.tb_challenge_revaluation (
    id SERIAL PRIMARY KEY,
    stud_id INT NOT NULL,
    course_id VARCHAR(100) NOT NULL,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    reval_request_id INT REFERENCES sch_exam.tb_revaluation_request(id),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Supplementary Exam
CREATE TABLE IF NOT EXISTS sch_exam.tb_supplementary_exam (
    id SERIAL PRIMARY KEY,
    inst_id INT NOT NULL,
    courses JSONB DEFAULT '[]'::jsonb,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    registration_window JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Reappear Exam
CREATE TABLE IF NOT EXISTS sch_exam.tb_reappear_exam (
    id SERIAL PRIMARY KEY,
    inst_id INT NOT NULL,
    term_id INT NOT NULL,
    courses JSONB DEFAULT '[]'::jsonb,
    reg_start DATE NOT NULL,
    reg_end DATE NOT NULL,
    exam_start DATE,
    exam_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. Malpractice Case
CREATE TABLE IF NOT EXISTS sch_exam.tb_malpractice_case (
    id SERIAL PRIMARY KEY,
    stud_id INT NOT NULL,
    schedule_id INT NOT NULL REFERENCES sch_exam.tb_exam_schedule(id),
    reported_by INT NOT NULL,
    description TEXT NOT NULL,
    committee VARCHAR(255),
    hearing_date DATE,
    verdict VARCHAR(100),
    status VARCHAR(50) DEFAULT 'reported',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
