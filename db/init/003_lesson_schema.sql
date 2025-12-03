-- 教科
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 教科と教師・クラスの紐づけ
CREATE TABLE subject_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    class_id INT NOT NULL,
    INDEX idx_subject_id (subject_id),
    INDEX idx_class_id (class_id)
);

-- 時間割
CREATE TABLE timetables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    major_id INT,
    date DATE NOT NULL,
    period INT NOT NULL,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    INDEX idx_class_id (class_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_teacher_id (teacher_id),
    CHECK (period BETWEEN 1 AND 7)
);

-- 授業時間
CREATE TABLE lessontime (
    id INT PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CHECK (id BETWEEN 1 AND 7)
);
