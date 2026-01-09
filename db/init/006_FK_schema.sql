-- 2. 外部キー追加（ALTER TABLEで）

-- classes の department_id, course_id, major_id, teacher_id
ALTER TABLE classes
    ADD CONSTRAINT fk_classes_department FOREIGN KEY (department_id) REFERENCES departments(id),
    ADD CONSTRAINT fk_classes_teacher FOREIGN KEY (teacher_id) REFERENCES teacher_users(user_id);

-- users の class_id
ALTER TABLE student_users
    ADD CONSTRAINT fk_users_class FOREIGN KEY (class_id) REFERENCES classes(id);

-- subject_assignments の外部キー
ALTER TABLE subject_assignments
    ADD CONSTRAINT fk_subject_assignments_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    ADD CONSTRAINT fk_subject_assignments_class FOREIGN KEY (class_id) REFERENCES classes(id);

-- timetables の外部キー
ALTER TABLE timetables
    ADD CONSTRAINT fk_timetables_class FOREIGN KEY (class_id) REFERENCES classes(id),
    ADD CONSTRAINT fk_timetables_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    ADD CONSTRAINT fk_timetables_teacher FOREIGN KEY (teacher_id) REFERENCES teacher_users(user_id);

-- 以下の外部キーはMySQLでは通常使わないのでコメントアウト（periodはlessontimeのidで参照しているため）
-- ALTER TABLE timetables
--    ADD CONSTRAINT fk_timetables_period FOREIGN KEY (period) REFERENCES lessontime(id);

-- attendance の外部キー（statusを拡張済み）
ALTER TABLE attendance
    ADD CONSTRAINT fk_attendance_user FOREIGN KEY (user_id) REFERENCES student_users(user_id),
    ADD CONSTRAINT fk_attendance_timetable FOREIGN KEY (timetable_id) REFERENCES timetables(id);

-- AIチャットボット関連
ALTER TABLE chat_logs
    ADD CONSTRAINT fk_chat_logs_user FOREIGN KEY (user_id) REFERENCES student_users(user_id);

-- notifications（配信対象）
ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_target_user FOREIGN KEY (target_user_id) REFERENCES student_users(user_id),
    ADD CONSTRAINT fk_notifications_department FOREIGN KEY (department_id) REFERENCES departments(id),
    ADD CONSTRAINT fk_notifications_class FOREIGN KEY (class_id) REFERENCES classes(id),
    ADD CONSTRAINT fk_notifications_major FOREIGN KEY (major_id) REFERENCES major(id);

-- notification_reads（既読）
ALTER TABLE notification_reads
    ADD CONSTRAINT fk_notification_reads_notification FOREIGN KEY (notification_id) REFERENCES notifications(id),
    ADD CONSTRAINT fk_notification_reads_user FOREIGN KEY (user_id) REFERENCES student_users(user_id);
