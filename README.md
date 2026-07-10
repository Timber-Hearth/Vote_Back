# SecretVote Backend

익명성과 운영성을 동시에 잡는 투표 백엔드입니다. 단순히 투표를 저장하는 API가 아니라, 인증된 생성자와 익명 참여자를 분리하고, Redis 기반 제한과 캐시, JWT 블랙리스트, Alembic 마이그레이션, Docker 기반 실행 환경, 그리고 GitHub 푸시를 기점으로 GCP가 자동 배포를 수행하는 이벤트 기반 운영 파이프라인까지 포함한 FastAPI 프로젝트입니다.

포트폴리오 관점에서 이 프로젝트의 핵심은 세 가지입니다.

- 익명 투표라는 도메인을 백엔드 중심으로 설계했다는 점
- 로컬 개발부터 컨테이너 실행, 스키마 버전 관리, 테스트까지 운영 흐름을 고려했다는 점
- FastAPI CRUD 수준을 넘어서 인증, 무결성, 캐시, 비동기 이벤트 처리, 자동 배포까지 함께 다뤘다는 점

## 프로젝트 개요

이 백엔드는 이런 원칙으로 설계되었습니다.

- 투표 생성자는 로그인한 사용자여야 한다.
- 투표 참여자는 회원가입 없이도 익명으로 참여할 수 있어야 한다.
- 동일 사용자의 중복 투표를 최소한의 식별 정보로 제어해야 한다.
- 투표 링크와 QR 기반 접근이 가능해야 한다.
- 결과적으로 서비스는 가볍게 시작할 수 있어야 하지만, 운영 환경으로 확장 가능한 구조여야 한다.

이를 위해 서버는 다음 방식으로 동작합니다.

- 생성자는 JWT 인증을 통해 투표 그룹을 만든다.
- 참여자는 QR 토큰 또는 토큰 URL로 투표 데이터를 조회한다.
- 참여자의 브라우저에는 익명 식별용 쿠키를 부여한다.
- 투표 데이터와 일부 공개 조회는 Redis 캐시를 사용한다.
- 로그아웃된 토큰은 Redis 블랙리스트에 올려 즉시 무효화한다.
- 데이터베이스 스키마는 Alembic으로 버전 관리한다.
- GitHub에 코드를 푸시하면 GCP가 이벤트를 감지해 자동 빌드 후 Cloud Run에 배포한다.
- 투표 생성 이벤트는 Pub/Sub로 발행되고, Cloud Function이 QR 이미지를 생성한 뒤 Cloud Storage에 저장한다.

## 왜 이 백엔드가 강한가

### 1. 익명성과 제어를 동시에 잡은 투표 설계

이 프로젝트는 완전 무상태 public write API가 아닙니다. 투표 생성 권한은 인증 사용자에게 제한하고, 투표 참여는 익명으로 열어두되 익명 UUID 쿠키를 사용해 중복 투표를 통제합니다. 즉, 관리 권한과 참여 권한을 분리한 구조입니다.

### 2. 서비스 운영에서 필요한 방어 장치가 이미 들어가 있음

- 로그인 시도 횟수 제한
- 회원가입 IP 기준 요청 제한
- 로그아웃 토큰 블랙리스트 처리
- bcrypt 길이 제한 검증
- DB 레벨 unique constraint를 통한 중복 투표 방지

### 3. 실행 환경을 재현 가능한 형태로 정리함

- Dockerfile 기반 앱 이미지 빌드
- PostgreSQL, Redis, App을 함께 띄우는 Docker Compose
- healthcheck 기반 의존 서비스 기동 순서 제어
- Alembic 기반 스키마 관리
- pytest 기반 회귀 테스트
- GitHub push 기반 GCP 자동 빌드 및 Cloud Run 배포
- Pub/Sub와 Cloud Function을 이용한 비동기 QR 이미지 생성 파이프라인

즉, "내 로컬에서만 되던 프로젝트"가 아니라 반복 가능한 환경에서 재실행 가능한 백엔드입니다.

## 핵심 기능

### 인증

- 회원가입
- 로그인
- JWT 발급
- 로그아웃 시 토큰 블랙리스트 등록

### 투표 생성 및 관리

- 로그인 사용자만 투표 그룹 생성 가능
- 다중 질문을 하나의 투표 그룹으로 구성 가능
- 질문별 복수 선택 허용 여부 설정 가능
- 투표 공개 여부, 종료 여부, 만료 시간, 삭제 시간 제어

### 익명 투표

- 비회원 참여 가능
- 익명 식별용 쿠키 자동 발급 및 정규화
- 동일 익명 사용자의 동일 항목 중복 투표 방지
- 잘못된 익명 쿠키가 들어와도 새 UUID를 발급해 복구

### 조회 및 클라우드 운영 기능

- QR 토큰 기반 투표 조회
- Redis 캐시 기반 공개 투표 조회 최적화
- GCS에 저장된 QR 이미지 조회 엔드포인트
- 투표 그룹 생성 시 Google Cloud Pub/Sub로 QR 생성 이벤트 발행
- Cloud Function이 이벤트를 소비해 QR 이미지를 생성하고 Cloud Storage에 저장
- GitHub push 이벤트를 시작점으로 GCP가 자동 빌드 후 Cloud Run에 배포

## 아키텍처

```mermaid
flowchart LR
    GH[GitHub Repository] --> TR[GCP Build Trigger]
    TR --> CB[Cloud Build]
    CB --> CR[Cloud Run]
    A[Client / Browser] --> B[FastAPI]
    B --> CR
    B --> C[Auth Router]
    B --> D[Poll Group Router]
    B --> E[Vote Router]
    B --> F[QR Router]
    C --> G[JWT / Password Hashing]
    D --> H[Service Layer]
    E --> H
    H --> I[Repository Layer]
    I --> J[(PostgreSQL)]
    C --> K[(Redis)]
    D --> K
    E --> K
    D --> L[Google Pub/Sub]
    L --> CF[Cloud Function]
    CF --> M[Google Cloud Storage]
    F --> M[Google Cloud Storage]
```

### 계층 분리 방식

- `src/api/v1/`: HTTP 엔드포인트, 요청/응답 정의, 상태코드 처리
- `src/services/`: 도메인 규칙과 비즈니스 로직
- `src/repositories/`: 데이터 접근과 영속성 처리
- `src/models/`: SQLAlchemy ORM 모델
- `src/schemas/`: Pydantic 요청/응답 스키마
- `src/core/`: DB, Redis, 보안, 공통 유틸리티
- `tests/`: 인증, 모델, 투표 시나리오 회귀 테스트

이 구조는 FastAPI 단일 파일 앱과 달리 책임을 분산시켜 변경 지점을 분명하게 만들고, 테스트와 유지보수를 쉽게 합니다.

## 도메인 모델

### User

- 로그인 식별자 `login_id`
- 해시된 비밀번호 `password_hash`

### PollGroup

투표 묶음의 최상위 엔티티입니다.

- 생성자 소유권 `owner_id`
- 외부 공유 토큰 `qr_token`
- 공개 결과 여부 `is_public_result`
- 종료 여부 `is_closed`
- 만료 시각 `expire_at`
- 자동 정리 기준 `delete_after_hours`

### Poll

PollGroup 안에 포함되는 개별 질문입니다.

- 질문 제목, 설명
- 복수 선택 허용 여부 `allow_multiple_choice`

### PollOption

질문별 선택지입니다.

- `poll_id` 기준 소속
- `display_order` 기준 정렬
- QR 토큰과 연결되는 `poll_group_qr`

### Vote

실제 투표 기록입니다.

- `poll_id`
- `option_id`
- `anonymous_id`
- `created_at`

DB 레벨에서는 `poll_id + anonymous_id + option_id` 조합에 unique constraint를 두어 동일 익명 사용자가 동일 선택지에 중복 투표하지 못하도록 막습니다.

## 요청 흐름

### 1. 회원가입 / 로그인 흐름

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant R as Redis
    participant DB as PostgreSQL

    U->>API: POST /auth/signup
    API->>R: IP 기준 가입 횟수 증가
    API->>DB: 사용자 중복 확인
    API->>DB: bcrypt 해시 저장
    API-->>U: success

    U->>API: POST /auth/login
    API->>R: login_id 기준 로그인 시도 횟수 증가
    API->>DB: 사용자 조회
    API->>API: 비밀번호 검증
    API->>R: 성공 시 로그인 제한 키 삭제
    API-->>U: JWT access token 발급
```

### 2. 투표 생성 흐름

```mermaid
sequenceDiagram
    participant Owner as Authenticated Owner
    participant API as FastAPI
    participant S as Service/Repo
    participant DB as PostgreSQL
    participant PS as Pub/Sub

    Owner->>API: POST /poll_group/create_poll_group
    API->>API: JWT 인증
    API->>S: 요청 데이터 검증
    S->>DB: PollGroup 생성
    S->>DB: Poll 생성
    S->>DB: PollOption 생성
    S->>PS: QR 생성용 이벤트 발행
    PS->>CF: 이벤트 전달
    CF->>GCS: QR PNG 저장
    API-->>Owner: success
```

### 3. 프로덕션 배포 흐름

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant GCP as GCP Trigger
    participant CB as Cloud Build
    participant CR as Cloud Run

    Dev->>GH: git push
    GH->>GCP: 저장소 이벤트 전달
    GCP->>CB: 빌드 시작
    CB->>CB: 컨테이너 이미지 빌드
    CB->>CR: 새 리비전 배포
    CR-->>Dev: 최신 백엔드 반영 완료
```

### 4. 익명 투표 흐름

```mermaid
sequenceDiagram
    participant V as Anonymous Voter
    participant API as FastAPI
    participant R as Redis
    participant DB as PostgreSQL

    V->>API: GET /poll_group/token/{token}
    API->>R: 캐시 조회
    alt cache hit
        R-->>API: poll data
    else cache miss
        API->>DB: PollGroup/Poll/Option 조회
        API->>R: 5분 캐시 저장
    end
    API-->>V: 투표 정보 반환

    V->>API: POST /vote/vote
    API->>API: anonymous_id 쿠키 확인 및 정규화
    API->>DB: 옵션 유효성 검증
    API->>DB: 투표 저장
    API-->>V: success + 필요 시 새 anonymous_id 쿠키 설정
```

## 기술 스택

### Backend

- Python 3.13
- FastAPI
- Uvicorn
- Pydantic v2

### Data Layer

- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Psycopg 3

### Caching / Session-like Controls

- Redis
- 로그인 제한
- 회원가입 제한
- 로그아웃 토큰 블랙리스트
- 공개 투표 데이터 캐시

### Security

- JWT (`python-jose`)
- bcrypt (`passlib`, `bcrypt`)
- OAuth2 Bearer Token

### Infra / Runtime

- Docker
- Docker Compose
- Healthcheck 기반 의존 서비스 기동 제어
- `.env` 기반 설정 로딩
- Cloud Run
- GCP 빌드 트리거 기반 자동 배포

### Cloud Extension Points

- Google Cloud Pub/Sub
- Google Cloud Functions
- Google Cloud Storage
- Cloud Build
- Cloud Run
- Cloud SQL Auth Proxy 기반 연결 시나리오 문서화

### Testing

- pytest
- FastAPI TestClient
- SQLite 기반 테스트 DB fixture
- Fake Redis 주입 방식의 단위/통합 혼합 테스트

## API 요약

현재 코드 기준 주요 엔드포인트는 아래와 같습니다.

### Auth

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/logout`

### Poll Group

- `GET /poll_group/token/{token}`
- `GET /poll_group/all_my_polls`
- `GET /poll_group/get_tokens`
- `POST /poll_group/create_poll_group`
- `POST /poll_group/close_poll_group`
- `POST /poll_group/open_poll_group`
- `POST /poll_group/change_delete_time/`
- `POST /poll_group/get_poll_settings`
- `POST /poll_group/edit_expire_time/`
- `POST /poll_group/set_public`

### Vote

- `POST /vote/vote`

### QR / Internal Ops

- `GET /qr/{token}`
- `POST /migration/internal/migrate`

## 데이터 무결성과 운영 포인트

이 프로젝트에서 신경 쓴 부분은 단순 기능보다도 "서비스가 망가지지 않게 만드는 장치"입니다.

### 1. 비밀번호 안전성

- bcrypt의 바이트 제한을 요청 스키마와 해시 함수 양쪽에서 검증
- 잘못된 길이의 비밀번호가 들어와도 조기 차단

### 2. 인증 공격 완화

- 로그인 실패 횟수를 Redis로 제한
- 회원가입 요청도 IP 단위로 제한

### 3. 토큰 무효화 전략

- 로그아웃 시 JWT 자체를 Redis 블랙리스트에 저장
- 만료 시각까지만 유지해 불필요한 저장을 줄임

### 4. 익명 투표의 현실적인 중복 방지

- 브라우저 쿠키 기반 anonymous UUID 관리
- 잘못된 쿠키는 새 UUID로 재발급
- DB unique constraint로 동일 옵션 재투표 방지

### 5. 읽기 부하 완화

- 공개 투표 조회는 Redis 캐시 우선
- 토큰 기반 투표 페이지 조회 시 DB hit를 줄일 수 있는 구조

## 실행 파이프라인

이 프로젝트는 이미 이벤트 기반 배포 파이프라인으로 운영되고 있습니다. 개발자가 GitHub에 코드를 push하면 GCP가 저장소 이벤트를 감지하고, 자동으로 빌드를 수행한 뒤 Cloud Run에 새 리비전을 배포합니다. 즉, 코드 변경부터 서비스 반영까지가 수동 배포가 아니라 클라우드 이벤트에 의해 이어지는 구조입니다.

### 프로덕션 CI/CD 파이프라인

```mermaid
flowchart LR
    A[Developer Push] --> B[GitHub Event]
    B --> C[GCP Trigger]
    C --> D[Cloud Build]
    D --> E[Container Image Build]
    E --> F[Cloud Run Deploy]
    F --> G[Serving New Revision]
```

### 프로덕션에서 실제로 강조할 수 있는 포인트

1. 소스코드 변경이 GitHub 이벤트로 시작된다.
2. GCP가 저장소 이벤트를 감지해 빌드 프로세스를 자동으로 시작한다.
3. 백엔드는 컨테이너 이미지로 패키징된다.
4. 새 이미지가 Cloud Run에 배포되며 revision 단위로 롤아웃된다.
5. 결과적으로 배포는 사람의 수동 서버 접속이 아니라 관리형 런타임 전환으로 처리된다.

### 백엔드가 제공하는 운영 단위

1. 의존성 설치
2. `.env` 로딩
3. PostgreSQL 연결
4. Redis 연결
5. Alembic 마이그레이션 적용
6. pytest 회귀 테스트 실행
7. Docker 이미지 빌드
8. 앱 컨테이너 실행

### QR 생성 비동기 파이프라인

```mermaid
flowchart LR
    A[PollGroup Created] --> B[Publish Pub/Sub Event]
    B --> C[Cloud Function Triggered]
    C --> D[Generate QR Image]
    D --> E[Store PNG in Cloud Storage]
    E --> F[Expose QR Public URL]
```

QR 이미지는 저장 이후 `GET /qr/{token}` 엔드포인트를 통해 조회되며, 응답에는 GCS public URL이 포함됩니다.

이 구조를 택한 이유는 명확합니다. 투표 생성 요청의 응답 시간을 QR 이미지 생성 작업과 분리해 API latency를 낮추고, 이미지 생성/저장을 별도 이벤트 소비자로 분리해 후처리를 독립적으로 확장하기 위해서입니다.

### 이 프로젝트에 맞는 운영 체크포인트

- lint 또는 static check 추가 가능
- pytest로 인증/투표 회귀 검증
- Docker build로 런타임 재현성 검증
- 배포 시점 Cloud Run revision 전환 여부 확인
- Pub/Sub 이벤트 발행 후 QR 이미지가 Cloud Storage에 적재되는지 확인
- 배포 후 `/docs` 또는 루트 엔드포인트 기반 스모크 테스트 수행

### 로컬/개발 실행 파이프라인

```mermaid
flowchart LR
    A[Developer] --> B[.env 준비]
    B --> C[PostgreSQL / Redis 기동]
    C --> D[alembic upgrade head]
    D --> E[pytest]
    E --> F[uvicorn src.main:app]
```

### 컨테이너 실행 파이프라인

`docker-compose.yml` 기준으로는 다음 순서로 시스템이 올라갑니다.

1. PostgreSQL 컨테이너 기동
2. Redis 컨테이너 기동
3. healthcheck 통과 확인
4. FastAPI 앱 컨테이너 시작

이 흐름은 의존 서비스 준비 전 앱이 먼저 떠서 실패하는 문제를 줄이는 실용적인 구성입니다.

## 로컬 실행 방법

### 1. 가상환경 생성

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 의존성 설치

`req.txt`는 UTF-16 인코딩이므로 일반 설치 명령을 그대로 사용하면 됩니다.

```bash
python -m pip install --upgrade pip
python -m pip install -r req.txt
```

### 3. 환경 변수 준비

프로젝트 루트에 `.env` 파일을 준비합니다.

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/vote_db
SECRET_KEY=replace-this-with-a-long-random-secret
REDIS_URL=redis://localhost:6379/0
```

### 4. DB / Redis 준비

```bash
docker run -d --name redis-local -p 6379:6379 redis:7-alpine
```

PostgreSQL은 로컬 설치 또는 Docker Compose를 사용하면 됩니다.

### 5. 마이그레이션 적용

```bash
alembic upgrade head
```

### 6. 테스트 실행

```bash
python -m pytest -q
```

### 7. 서버 실행

```bash
uvicorn src.main:app --reload
```

Swagger UI:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Docker 실행

### Docker Compose

가장 재현성 높은 실행 방법입니다.

```bash
docker compose up --build
```

백그라운드 실행:

```bash
docker compose up -d --build
```

중지:

```bash
docker compose down
```

### Dockerfile 기반 단독 실행

```bash
docker build -t secretvote-backend:latest .
docker run --rm -p 8080:8080 \
  -e DATABASE_URL="postgresql+psycopg://USER:PASSWORD@host.docker.internal:5432/vote_db" \
  -e SECRET_KEY="replace-this" \
  -e REDIS_URL="redis://host.docker.internal:6379/0" \
  secretvote-backend:latest
```

## 테스트 전략

이 프로젝트는 기능만 만들고 끝내지 않고, 실패하기 쉬운 지점을 테스트로 고정하고 있습니다.

### 검증하는 내용

- bcrypt 허용 길이 초과 시 요청 차단
- 로그인/회원가입 request schema alias 처리
- 모델 테이블과 unique constraint 등록 여부
- 다중 선택 투표 저장
- 동일 옵션 중복 투표 거부
- 잘못된 anonymous cookie 자동 복구

### 테스트 방식

- FastAPI TestClient로 HTTP 레벨 검증
- SQLite fixture로 빠른 DB 테스트
- Fake Redis 객체 주입으로 외부 의존성 없이 Redis 동작 모사

이 접근은 테스트 속도를 확보하면서도 실제 엔드포인트 동작에 가까운 회귀 검증을 가능하게 합니다.

## 이 프로젝트에서 보여주고 싶은 백엔드 역량

이 저장소는 단순한 "FastAPI 써봤다" 수준의 결과물이 아닙니다. 아래 역량을 한 프로젝트 안에 묶어 보여주기 위해 설계했습니다.

- 인증과 익명 참여를 동시에 만족하는 권한 모델 설계
- DB 무결성과 애플리케이션 로직을 함께 사용하는 데이터 보호 전략
- 캐시, 토큰 블랙리스트, 요청 제한 같은 운영형 방어 장치 구현
- 스키마 버전 관리와 컨테이너 기반 실행 환경 구성
- 테스트 가능한 구조로 서비스/저장소/라우터 분리
- GitHub 이벤트 기반 자동 빌드와 Cloud Run 배포 파이프라인 구성
- Pub/Sub, Cloud Function, GCS를 연결한 비동기 QR 생성 이벤트 아키텍처 구현
- Cloud SQL, Cloud Run, Pub/Sub, GCS를 묶은 GCP 중심 운영 구조 설계

## 개선 예정 항목

현재 구조만으로도 포트폴리오 제출에는 충분히 강하지만, 실제 서비스 수준으로 더 끌어올릴 수 있는 다음 단계도 분명합니다.

- GitHub Actions 또는 Cloud Build 기반 CI/CD 워크플로 추가
- 인증/권한 관련 통합 테스트 확대
- observability를 위한 structured logging 및 metrics 추가
- `/migration/internal/migrate` 같은 내부 엔드포인트 보호 강화
- 캐시 무효화 전략 정교화
- poll_group 관련 예외 처리 정리 및 응답 일관성 강화

## 한 줄 정리

SecretVote Backend는 익명 투표라는 도메인을 FastAPI, PostgreSQL, Redis, Alembic, Docker, 테스트 전략 위에 실전형으로 풀어낸 백엔드 프로젝트입니다. 기능 구현, 데이터 무결성, 인증 보안, 운영 재현성, 클라우드 확장성을 한 저장소 안에서 함께 보여주는 것이 이 프로젝트의 핵심 가치입니다.