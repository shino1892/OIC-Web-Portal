CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100) ,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('student','teacher','admin') NOT NULL,
    class_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_first BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_class_id (class_id)
);
