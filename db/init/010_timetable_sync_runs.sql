-- 同期の実行状態（初回同期の通知抑制・失敗監視用）
CREATE TABLE IF NOT EXISTS timetable_sync_runs (
    department_id INT PRIMARY KEY,
    last_run_at DATETIME NULL,
    last_success_at DATETIME NULL,
    last_status VARCHAR(20) NOT NULL DEFAULT 'never',
    last_error TEXT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
