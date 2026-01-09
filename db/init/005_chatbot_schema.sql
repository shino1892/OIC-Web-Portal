-- FAQ（質問・回答管理）
CREATE TABLE faq (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- AIチャットログ
CREATE TABLE chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 通知（授業変更や出席リマインド、イベント、その他）
-- 配信対象は scope + (target_user_id / department_id / class_id / major_id) で表現
-- 既読は notification_reads でユーザー単位に管理
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    scope ENUM('ALL','USER','DEPARTMENT','CLASS') NOT NULL,
    target_user_id INT NULL,
    department_id INT NULL,
    class_id INT NULL,
    major_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_notifications_scope_created (scope, created_at),
    INDEX idx_notifications_target_user (target_user_id),
    INDEX idx_notifications_department (department_id),
    INDEX idx_notifications_class_major (class_id, major_id)
);

-- 既読管理（ユーザーごと）
CREATE TABLE notification_reads (
    notification_id INT NOT NULL,
    user_id INT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id, user_id),
    INDEX idx_notification_reads_user (user_id)
);
