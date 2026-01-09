# Copilot instructions (OIC-Web-Portal)

## 全体像（Docker 前提）

- 本番/開発とも `docker-compose.yml` を中心に、`nginx`(80) → `frontend`(Next.js 3000) / `backend`(Flask 5000) → `db`(MySQL 3306) の構成。
- OAuth ログインは **Nginx 経由の `http://localhost/` アクセス前提**（フロントは相対パス `/api/...` を叩くため）。例: `frontend/src/app/login/page.tsx` は `fetch("/api/users/auth/google")`。

## 起動・初期化（よく使う操作）

- 起動: `docker compose up --build`
- DB 再初期化（スキーマ/初期データの入れ直し）: `docker compose down -v` → 再度 `up --build`
- DB 初期化 SQL: `db/init/*.sql`（初回起動時に実行）

## Frontend（Next.js App Router）

- 画面は `frontend/src/app/**/page.tsx` に配置（App Router）。共通 UI は `frontend/src/components/`。
- API 呼び出しは `fetch` ベース。認証付きは `frontend/src/hooks/useAuthFetch.ts` を使い、`Authorization: Bearer <token>` を付与。
- 401 時の挙動は統一（token 削除 → `auth-change` イベント → `/login` へ遷移）。
- Google ログインは `NEXT_PUBLIC_GOOGLE_CLIENT_ID` を参照（`frontend/src/app/login/page.tsx`）。

## Backend（Flask + Blueprint + PyMySQL）

- エントリ: `backend/wsgi.py` → `backend/app/__init__.py:create_app()`。
- ルーティングは `backend/app/api/*.py` の Blueprint を `create_app()` で登録し、URL は `url_prefix` で `/api/...` に揃える（例: `/api/users`, `/api/timetables`）。
- DB アクセスは SQLAlchemy ではなく、主に `backend/app/utility/db/` の PyMySQL ユーティリティ経由（`db_connect()` で DictCursor）。各ドメインごとに `db_user.py`, `db_attendance.py` 等へ関数追加。
- DB 関数の書き方は既存に合わせる（`with conn.cursor()`、必要なら `conn.commit()`、例外時 `rollback()`、`finally` で `conn.close()`）。

## 認証（このプロジェクト固有の前提）

- バックエンドは Google ID トークン検証後に **独自 JWT** を発行（`backend/app/api/user_routes.py` + `backend/app/utility/auth/jwt.py`）。
- API は基本 `Authorization: Bearer <jwt>` を要求し、`decode_access_token()` が `None` を返したら 401。
- 設定値は `backend/app/core/config.py` が環境変数から読む（`DATABASE_*`, `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY` 等）。

## Scheduler（時間割同期）

- `scheduler` コンテナは `python -m app.scheduler.run_scheduler` を実行（`docker-compose.yml`）。
- 定期処理は APScheduler で `sync_all_departments()` を 06:00/18:00 に実行（`backend/app/scheduler/run_scheduler.py`）。

## 変更を入れる場所の目安

- API 追加/変更: `backend/app/api/` + 必要に応じて `backend/app/utility/db/`。
- フロント画面追加: `frontend/src/app/<route>/page.tsx`。
- リバースプロキシ/API 経路: `docker/nginx/default.conf`（`/api/` は backend へ）。
