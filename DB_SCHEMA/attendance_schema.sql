CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    timetable_id INT NOT NULL,
    status ENUM('出席','欠席','遅刻','早退','公欠') NOT NULL,
    marked_by INT NOT NULL,
    marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_timetable_id (timetable_id),
    INDEX idx_marked_by (marked_by),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (timetable_id) REFERENCES timetables(id),
    FOREIGN KEY (marked_by) REFERENCES users(user_id)
);
