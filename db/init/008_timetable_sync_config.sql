-- 学科ごとのスプレッドシート設定
CREATE TABLE department_spreadsheets (
    department_id INT PRIMARY KEY,
    spreadsheet_id VARCHAR(128) NOT NULL,
    worksheet_name VARCHAR(128) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- シート上の専攻表記（別名）→ DB上の専攻名（正規名）へのマッピング
CREATE TABLE major_aliases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    alias_name VARCHAR(100) NOT NULL,
    canonical_major_name VARCHAR(100) NOT NULL,
    UNIQUE KEY uq_major_alias (department_id, alias_name),
    INDEX idx_major_alias_department (department_id)
);

-- 初期設定（例：情報スペシャリスト学科）
INSERT INTO department_spreadsheets (department_id, spreadsheet_id, worksheet_name, enabled)
VALUES (110, '1KhKedobg51enXuJg8ggGQDrCKHwNWsILz1JourFVa5A', '情スペ', TRUE)
ON DUPLICATE KEY UPDATE spreadsheet_id=VALUES(spreadsheet_id), worksheet_name=VALUES(worksheet_name), enabled=VALUES(enabled);

-- 専攻の別名（例：シート上の "SC専攻" / "AI専攻" をDBの正規名へ）
INSERT INTO major_aliases (department_id, alias_name, canonical_major_name)
VALUES
    (110, 'SC専攻', 'ネットワーク・セキュリティ専攻'),
    (110, 'AI専攻', 'AI・IoT専攻'),
    (110, '1年SC専攻', 'ネットワーク・セキュリティ専攻'),
    (110, '2年SC専攻', 'ネットワーク・セキュリティ専攻'),
    (110, '3年SC専攻', 'ネットワーク・セキュリティ専攻'),
    (110, '1年AI専攻', 'AI・IoT専攻'),
    (110, '2年AI専攻', 'AI・IoT専攻'),
    (110, '3年AI専攻', 'AI・IoT専攻')
ON DUPLICATE KEY UPDATE canonical_major_name=VALUES(canonical_major_name);
