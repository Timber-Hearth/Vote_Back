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
DATABASE_URL=postgresql+psycopg://postgres:<DB_PASSWORD>@localhost:5432/vote_db
SECRET_KEY=<YOUR_SECRET_KEY>
```

`SECRET_KEY` 생성 예시:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 2-6. PostgreSQL DB 준비

기본 접속 후 DB 생성:

```powershell
psql -U postgres
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
DATABASE_URL=postgresql+psycopg://postgres:<DB_PASSWORD>@localhost:5432/vote_db
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
psql -U postgres -d postgres
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
