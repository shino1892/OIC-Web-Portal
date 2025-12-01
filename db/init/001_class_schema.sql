-- 学科
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(100),
    CONSTRAINT ck_id CHECK (id BETWEEN 100 AND 999)
);

CREATE TABLE major (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL
);

-- クラス
CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    teacher_id INT ,
    INDEX idx_department_id (department_id),
    INDEX idx_teacher_id (teacher_id)
);


