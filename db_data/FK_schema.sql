-- 2. 外部キー追加（ALTER TABLEで）

-- courses と majors の department_id
ALTER TABLE courses
    ADD CONSTRAINT fk_courses_department FOREIGN KEY (department_id) REFERENCES departments(id);

ALTER TABLE majors
    ADD CONSTRAINT fk_majors_department FOREIGN KEY (department_id) REFERENCES departments(id);

-- classes の department_id, course_id, major_id, teacher_id
ALTER TABLE classes
    ADD CONSTRAINT fk_classes_department FOREIGN KEY (department_id) REFERENCES departments(id),
    ADD CONSTRAINT fk_classes_course FOREIGN KEY (course_id) REFERENCES courses(id),
    ADD CONSTRAINT fk_classes_major FOREIGN KEY (major_id) REFERENCES majors(id),
    ADD CONSTRAINT fk_classes_teacher FOREIGN KEY (teacher_id) REFERENCES users(user_id);

-- users の class_id
ALTER TABLE users
    ADD CONSTRAINT fk_users_class FOREIGN KEY (class_id) REFERENCES classes(id);

-- subject_assignments の外部キー
ALTER TABLE subject_assignments
    ADD CONSTRAINT fk_subject_assignments_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    ADD CONSTRAINT fk_subject_assignments_teacher FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    ADD CONSTRAINT fk_subject_assignments_class FOREIGN KEY (class_id) REFERENCES classes(id);

-- timetables の外部キー
ALTER TABLE timetables
    ADD CONSTRAINT fk_timetables_class FOREIGN KEY (class_id) REFERENCES classes(id),
    ADD CONSTRAINT fk_timetables_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    ADD CONSTRAINT fk_timetables_teacher FOREIGN KEY (teacher_id) REFERENCES users(user_id);

-- 以下の外部キーはMySQLでは通常使わないのでコメントアウト（periodはlessontimeのidで参照しているため）
-- ALTER TABLE timetables
--    ADD CONSTRAINT fk_timetables_period FOREIGN KEY (period) REFERENCES lessontime(id);

-- attendance の外部キー（statusを拡張済み）
ALTER TABLE attendance
    ADD CONSTRAINT fk_attendance_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    ADD CONSTRAINT fk_attendance_timetable FOREIGN KEY (timetable_id) REFERENCES timetables(id),
    ADD CONSTRAINT fk_attendance_marked_by FOREIGN KEY (marked_by) REFERENCES users(user_id);

-- AIチャットボット関連
ALTER TABLE chat_logs
    ADD CONSTRAINT fk_chat_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id);

ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(user_id);
