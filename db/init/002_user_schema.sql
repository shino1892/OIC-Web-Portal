CREATE TABLE student_users (
    user_id INT PRIMARY KEY UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    google_sub VARCHAR(255) NOT NULL UNIQUE,
    admission_year INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    class_id INT NOT NULL,
    major_id INT,
    is_repeat BOOLEAN NOT NULL DEFAULT FALSE,
    is_graduation BOOLEAN NOT NULL DEFAULT FALSE,
    is_enrollment BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_class_id (class_id)
);

CREATE TABLE teacher_users (
    user_id INT PRIMARY KEY UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    google_sub VARCHAR(255) UNIQUE,
    full_name VARCHAR(100) NOT NULL
);