-- ユーザーとFeliCa IDmの紐付けテーブル
-- 1人のユーザーが複数のカードを持てるように別テーブルで管理
CREATE TABLE IF NOT EXISTS user_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    felica_idm VARCHAR(16) NOT NULL UNIQUE,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES student_users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_felica_idm (felica_idm)
);

-- 入構記録テーブルの作成
CREATE TABLE IF NOT EXISTS entry_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    felica_idm VARCHAR(16) NOT NULL,
    entered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_id VARCHAR(50),
    INDEX idx_felica_idm (felica_idm),
    INDEX idx_entered_at (entered_at)
);
