# SecretVote Backend

## 1) 프로젝트 풀이

이 저장소는 **익명 투표 백엔드 API**를 만드는 FastAPI 기반 프로젝트입니다.
현재 코드 기준으로 핵심 구현 범위는 아래와 같습니다.

- 사용자 인증: 회원가입/로그인 + JWT 발급
- 투표 생성: 제목/설명/옵션/삭제 시간 설정
- QR 토큰 발급: 투표 생성 시 접근 토큰 생성
- 투표 조회: 토큰으로 투표 조회
- DB 마이그레이션: Alembic으로 스키마 관리
- 기본 테스트: 인증/모델/투표 생성 로직 테스트

### 현재 주요 엔드포인트

- `POST /auth/signup`
- `POST /auth/login`
- `POST /polls/create`
- `GET /polls/{token}`

### 코드 구조 요약

- `src/main.py`: FastAPI 앱 생성, 라우터 등록
- `src/api/v1/`: 엔드포인트
- `src/services/`: 비즈니스 로직
- `src/models/`: SQLAlchemy 모델
- `src/schemas/`: Pydantic 요청/응답 스키마
- `src/core/`: DB/JWT 보안 공통 설정
- `alembic/`: 마이그레이션
- `tests/`: pytest 테스트

---

## 2) 완전히 포맷한 컴퓨터에서 작업 환경 재구축 (Windows, IDE 설치 완료 가정)

아래 순서를 그대로 따르면 됩니다.

### 2-1. 사전 설치

1. **Git**
2. **Python 3.13.x** (현재 프로젝트 테스트/캐시 기준 3.13 사용 흔적)
3. **PostgreSQL 17** (현재 `local_db_start.bat` 서비스명 `postgresql-x64-17` 기준)

버전 확인:

```powershell
python --version
git --version
psql --version
```

### 2-2. 프로젝트 받기

```powershell
git clone <your-repository-url> E:\SecretVote\backend
Set-Location E:\SecretVote\backend
```

### 2-3. 가상환경 생성/활성화

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2-4. 의존성 설치

```powershell
python -m pip install -r req.txt
```

참고:

- 현재 `req.txt`는 UTF-16 LE BOM 형식이지만, 현재 환경에서는 `pip install -r req.txt`가 정상 동작 확인됨.

### 2-5. 환경변수 파일 준비 (`.env`)

프로젝트 루트(`E:\SecretVote\backend`)에 `.env` 생성:

```dotenv
DATABASE_URL=postgresql+psycopg://ggwp:<DB_PASSWORD>@localhost:5432/vote_db
SECRET_KEY=<YOUR_SECRET_KEY>
```

`SECRET_KEY` 생성 예시:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 2-6. PostgreSQL DB 준비

기본 접속 후 DB 생성:

```powershell
psql -U ggwp
```

```sql
CREATE DATABASE vote_db;
\c vote_db
```

필요하면 서비스 재시작:

```powershell
.\local_db_start.bat
```

### 2-7. 마이그레이션 반영

```powershell
alembic upgrade head
```

### 2-8. `PYTHONPATH` 설정 (중요)

이 코드베이스는 import 경로 특성상 `PYTHONPATH`에 `src`가 있어야 안정적으로 동작합니다.

현재 세션만 설정:

```powershell
$env:PYTHONPATH="E:\SecretVote\backend\src"
```

영구 설정(새 터미널부터 반영):

```powershell
setx PYTHONPATH "E:\SecretVote\backend\src"
```

### 2-9. 서버 실행

```powershell
Set-Location E:\SecretVote\backend
$env:PYTHONPATH="E:\SecretVote\backend\src"
uvicorn src.main:app --reload
```

문서 확인:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 2-10. 테스트 실행

```powershell
Set-Location E:\SecretVote\backend
$env:PYTHONPATH="E:\SecretVote\backend\src"
python -m pytest -q
```

현재 기준 검증 결과: `14 passed`.

### 2-11. macOS 기준 재구축 (Apple Silicon/Intel)

아래는 macOS에서 같은 개발환경을 맞추는 절차입니다.

#### A) 사전 설치

1. **Homebrew**
2. **Python 3.13.x**
3. **PostgreSQL 17**
4. (선택) **Git**

버전 확인:

```bash
python3 --version
git --version
psql --version
```

Homebrew가 없다면:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 예시:

```bash
brew install python@3.13
brew install postgresql@17
brew services start postgresql@17
```

#### B) 프로젝트/가상환경

```bash
git clone <your-repository-url> ~/SecretVote/backend
cd ~/SecretVote/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r req.txt
```

#### C) 환경변수 파일

프로젝트 루트(`~/SecretVote/backend`)에 `.env` 생성:

```dotenv
DATABASE_URL=postgresql+psycopg://ggwp:<DB_PASSWORD>@localhost:5432/vote_db
SECRET_KEY=<YOUR_SECRET_KEY>
```

`SECRET_KEY` 생성:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

#### D) PostgreSQL DB 생성

Homebrew 기본 설정에서는 현재 macOS 사용자로 바로 접속되는 경우가 많습니다.

```bash
psql postgres
```

```sql
CREATE DATABASE vote_db;
\c vote_db
```

만약 `postgres` 계정으로 접속해야 하는 환경이면 아래처럼 시도:

```bash
psql -U ggwp -d postgres
```

#### E) 마이그레이션 + PYTHONPATH + 실행

이 코드베이스는 import 경로 특성상 `PYTHONPATH`에 `src`를 추가해야 안정적으로 동작합니다.

현재 터미널 세션:

```bash
export PYTHONPATH="$(pwd)/src"
```

실행/테스트:

```bash
alembic upgrade head
python -m pytest -q
uvicorn src.main:app --reload
```

영구 설정(`~/.zshrc`):

```bash
echo 'export PYTHONPATH="$HOME/SecretVote/backend/src"' >> ~/.zshrc
source ~/.zshrc
```

확인:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 3) 트러블슈팅 체크리스트

- `ModuleNotFoundError: No module named 'core'` 또는 `'models'`
  - 원인: `PYTHONPATH` 미설정
  - 해결: `$env:PYTHONPATH="E:\SecretVote\backend\src"`

- `401 invalid token`
  - 원인: `SECRET_KEY` 불일치/누락, 토큰 만료
  - 해결: `.env`의 `SECRET_KEY` 확인 후 서버 재시작

- DB 접속 실패
  - 원인: PostgreSQL 서비스 중지, 비밀번호/포트 불일치
  - 해결: 서비스 상태 확인, `.env`의 `DATABASE_URL` 점검

- 마이그레이션 실패
  - 원인: DB 미생성 또는 URL 오타
  - 해결: DB 생성 후 `alembic upgrade head` 재실행

---

## 4) 빠른 재구축 요약

```powershell
Set-Location E:\SecretVote\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r req.txt
$env:PYTHONPATH="E:\SecretVote\backend\src"
alembic upgrade head
python -m pytest -q
uvicorn src.main:app --reload
```

### macOS 빠른 재구축

```bash
cd ~/SecretVote/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r req.txt
export PYTHONPATH="$(pwd)/src"
alembic upgrade head
python -m pytest -q
uvicorn src.main:app --reload
```

## 5) Cloud SQL (GCP) 연결 가이드

Cloud SQL 인스턴스를 **비공개 IP**로 만든 경우, 로컬에서 직접 접속이 불가합니다.
Cloud SQL Auth Proxy를 통해 로컬 ↔ Cloud SQL 터널을 열어야 합니다.

### 5-1. Cloud SQL Auth Proxy 설치 (Windows)

[공식 다운로드 페이지](https://cloud.google.com/sql/docs/postgres/sql-proxy#install)에서 Windows용 `.exe` 다운로드 후 적당한 위치에 저장합니다.

또는 gcloud 로그인 후 아래 명령어로 다운로드:

```powershell
# gcloud 로그인 (처음 한 번)
gcloud auth login
gcloud auth application-default login
```

### 5-2. 프록시 실행

```powershell
./cloud-sql-proxy --port=5433 <PROJECT_ID>:<REGION>:<INSTANCE_ID>
```

예시:
```powershell
./cloud-sql-proxy --port=5433 secret-vote-back:us-central1:secretvote-db
```

프록시가 실행되면 `localhost:5433`으로 Cloud SQL에 접속 가능해집니다.
docker run -d --name redis-local -p 6379:6379 redis:7-alpine

로컬로 db 세팅할때 레디스 켜야함 이 명령어를 써라
docker run -d --name redis-local -p 6379:6379 redis:7-alpine

### 5-3. .env 설정 (Cloud SQL 연결용)

```dotenv
DATABASE_URL=postgresql+psycopg://ggwp:!Qogusdn90@127.0.0.1:5433/vote_db
SECRET_KEY=<YOUR_SECRET_KEY>
REDIS_URL=redis://<REDIS_HOST>:6379/0
```

### 5-4. DB/유저 생성 (최초 1회)

프록시 켜놓은 상태에서 `psql`로 접속:

```powershell
psql -h 127.0.0.1 -p 5433 -U postgres -d postgres
psql -h 127.0.0.1 -p 5433 -U ggwp -d vote_db
```

```sql
CREATE DATABASE vote_db;
CREATE USER ggwp WITH PASSWORD '강한비밀번호';
GRANT ALL PRIVILEGES ON DATABASE vote_db TO ggwp;
\q
```

### 5-4-1. 마이그레이션 권한 설정 (중요)

Alembic 마이그레이션 실행 전에 `ggwp` 사용자에게 스키마 권한을 미리 설정해야 합니다.
(`permission denied for schema public` 에러 방지용)

프록시 켜놓은 상태에서 `psql`로 다시 접속:

```powershell
psql -h 127.0.0.1 -p 5433 -U postgres -d vote_db
```

**아래 명령어들을 차례대로 실행:**

```sql
-- 1. 스키마에 대한 기본 권한 부여
GRANT USAGE ON SCHEMA public TO ggwp;
GRANT CREATE ON SCHEMA public TO ggwp;

-- 2. 기존 테이블/시퀀스에 권한 부여 (나중에 만들어질 테이블도 포함)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ggwp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ggwp;

-- 3. 미래에 생성될 테이블/시퀀스도 자동으로 권한 부여 (default privileges)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ggwp;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ggwp;

-- 4. 데이터베이스 자체 권한도 명시적으로 부여
GRANT CONNECT ON DATABASE vote_db TO ggwp;
GRANT TEMP ON DATABASE vote_db TO ggwp;

\q
```

**참고:**
- `GRANT USAGE ON SCHEMA public`: 스키마 접근 권한
- `GRANT CREATE ON SCHEMA public`: 스키마 내에서 테이블 생성 권한
- `ALTER DEFAULT PRIVILEGES`: 앞으로 생성될 네 객체에 대한 자동 권한 부여

이 설정 후에는 Alembic 마이  레이션이 정상 작동합니다.

### 5-5. Alembic 마이그레이션 적용

테이블을 수동으로 만들 필요 없이, Alembic이 모델 기준으로 자동 생성합니다.

**로컬 PowerShell에서:**

```powershell
Set-Location E:\SecretVote\backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="E:\SecretVote\backend\src"
alembic upgrade head
```

예상 출력:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> b6562685d049, init
INFO  [alembic.runtime.migration] Running upgrade b6562685d049 -> 051b595f8b2c, add default uuid for qr_tokens id
INFO  [alembic.runtime.migration] Running upgrade 051b595f8b2c -> aff56d16c962, vote table change
INFO  [alembic.runtime.migration] Running upgrade aff56d16c962 -> b593a6a9b9ac, user table's id auto increase
```

**완료 후 테이블 확인:**

```powershell
psql -h 127.0.0.1 -p 5433 -U ggwp -d vote_db
```

```sql
\dt
```

`users`, `polls`, `poll_options`, `votes`, `qr_tokens`, `alembic_version` 6개 테이블이 나오면 완료.

### 5-5-1. 로컬 백엔드 시작 및 테스트

프록시는 계속 켜놓은 상태에서 **새 PowerShell 터미널**을 열어 서버를 실행합니다:

```powershell
Set-Location E:\SecretVote\backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="E:\SecretVote\backend\src"
uvicorn src.main:app --reload
```

예상 출력:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**기본 스모크 테스트 (Swagger UI 또는 curl/Postman):**

1. **회원가입**
   - `POST /api/v1/auth/register`
   - Body: `{"login_id": "testuser", "password": "testpass123"}`
   - 응   : 사용자 생성 성공

2. **로그인**
   - `POST /api/v1/auth/login`
   - Body: `{"login_id": "testuser", "password": "testpass123"}`
   - 응답: `{"access_token": "..."}`

3. **API 문서 확인**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

모두 정상이면 로컬 앱 + Cloud DB 연결 완료.

---

## 6) Docker 실행

`Dockerfile`은 FastAPI 앱(`src.main:app`)을 PostgreSQL 연결 전제로 실행합니다.

### 6-1. 이미지 빌드

```powershell
docker build -t secretvote-backend:latest .
```

### 6-2. 컨테이너 실행

로컬 PostgreSQL을 사용할 때는 `host.docker.internal`를 사용하면 됩니다.

```powershell
docker run --rm -p 8000:8000 `
  -e DATABASE_URL="postgresql+psycopg://ggwp:<DB_PASSWORD>@host.docker.internal:5432/vote_db" `
  -e SECRET_KEY="<YOUR_SECRET_KEY>" `
  secretvote-backend:latest
```

확인:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 6-3. Docker Compose로 한 번에 실행

`docker compose up` 한 번으로 `app + postgres`를 같이 올릴 수 있습니다.

처음 한 번(선택):

```powershell
Copy-Item .env.compose.example .env.compose
```

실행:

```powershell
docker compose --env-file .env.compose up --build
```

백그라운드 실행:

```powershell
docker compose --env-file .env.compose up -d --build
```

중지/정리:

```powershell
docker compose down
docker compose down -v
```
