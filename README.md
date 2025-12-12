# OIC-Web-Portal

学生の学校生活をサポートするための統合管理システムです。出席管理、時間割表示、AI チャットボットによるサポート機能などを提供します。

## 🚀 機能一覧

- **出席管理**:
  - 日々の出席・欠席・遅刻・早退・公欠の記録と確認。
  - 出席率の自動計算と警告表示（出席率 80%未満）。
  - Web 上からの欠席・遅刻・早退・公欠の申請。
  - FeliCa カード（学生証）による入退室記録（バックエンド対応）。
- **時間割表示**:
  - 個人の履修状況に合わせた時間割の表示。
  - 各授業の出席ステータスの可視化。
- **AI サポート**:
  - 学校生活に関する質問に答える AI チャットボット（開発中）。
- **ユーザー認証**:
  - Google OAuth を使用したログイン。

## 🛠️ 技術スタック

### Frontend

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Fetch API (Custom hooks)

### Backend

- **Framework**: Flask (Python)
- **Database Driver**: PyMySQL
- **Authentication**: Google OAuth / JWT

### Database

- **RDBMS**: MySQL 8.0
- **Schema Management**: Docker entrypoint init scripts

### Infrastructure

- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (Reverse Proxy)

## 📦 セットアップ手順

### 前提条件

- Docker Desktop がインストールされていること。
- Git がインストールされていること。

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd OIC-Web-Portal
```

### 2. 環境変数の設定

各ディレクトリにある `.env.example` をコピーして `.env` ファイルを作成し、必要な値を設定してください。

**Frontend (`frontend/.env`)**

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

**Backend (`backend/.env`)**

```env
FLASK_APP=app
FLASK_DEBUG=1
DATABASE_HOST=db
DATABASE_USER=devuser
DATABASE_PASSWORD=sanda3
DATABASE_NAME=campus_life
SECRET_KEY=your_secret_key
# Google OAuth settings
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 3. アプリケーションの起動

Docker Compose を使用してコンテナをビルド・起動します。

```bash
docker compose up --build
```

初回起動時はデータベースの初期化スクリプト（`db/init/*.sql`）が実行され、テーブル作成と初期データの投入が行われます。

## 🌐 アクセス方法

nginxでのリバースプロキシを行なっているので必ず[http://localhost](http://localhost)からアクセスしてください、ログインが正常に行われません。

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5000](http://localhost:5000)
- **Nginx**: [http://localhost](http://localhost)
- **Database**: Host: `localhost`, Port: `65533` (User: `devuser`, Pass: `sanda3`)

## 📂 ディレクトリ構成

```
Sanda-Factory/
├── backend/                # Flask APIサーバー
│   ├── app/
│   │   ├── api/            # ルート定義 (Endpoints)
│   │   ├── core/           # 設定関連
│   │   └── utility/        # DB接続、認証などのユーティリティ
│   └── docker/             # Backend用Dockerfile
├── frontend/               # Next.js フロントエンドアプリケーション
│   ├── src/
│   │   ├── app/            # App Router ページコンポーネント
│   │   ├── components/     # 共通コンポーネント
│   │   └── hooks/          # カスタムフック
│   └── docker/             # Frontend用Dockerfile
├── db/                     # データベース関連
│   ├── init/               # 初期化SQLスクリプト (Schema & Data)
│   └── Dockerfile
├── docker/                 # 共通Docker設定 (Nginxなど)
└── docker-compose.yml      # コンテナ構成定義
```

## 📝 開発フロー

1.  **データベースの変更**: `db/init/` に新しい SQL ファイルを追加するか、既存のスキーマを変更してボリュームを再作成してください。
2.  **API の追加**: `backend/app/api/` に新しいルートファイルを作成し、`backend/app/__init__.py` で Blueprint を登録します。
3.  **ページの追加**: `frontend/src/app/` フォルダ構造に従って `page.tsx` を作成します。

## 🐛 トラブルシューティング

- **DB 接続エラー**: コンテナが完全に立ち上がるまで時間がかかる場合があります。数秒待ってからリトライしてください。
- **データが反映されない**: `docker compose down -v` を実行してボリュームを削除し、再度 `up` して初期データを再投入してください。
