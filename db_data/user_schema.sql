CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('student','teacher','admin') NOT NULL,
    class_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_first BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_class_id (class_id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
