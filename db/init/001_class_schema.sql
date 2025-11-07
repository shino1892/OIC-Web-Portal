-- 学科
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- コース
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    INDEX idx_department_id (department_id)
);

-- 専攻
CREATE TABLE majors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    INDEX idx_department_id (department_id)
);

-- クラス
CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade INT NOT NULL,
    group_num INT,
    department_id INT NOT NULL,
    course_id INT,
    major_id INT,
    teacher_id INT,
    INDEX idx_department_id (department_id),
    INDEX idx_course_id (course_id),
    INDEX idx_major_id (major_id),
    INDEX idx_teacher_id (teacher_id),
    CHECK (
        (course_id IS NOT NULL AND major_id IS NULL) OR
        (course_id IS NULL AND major_id IS NOT NULL) OR
        (course_id IS NULL AND major_id IS NULL)
    )
);

