# SecretVote Backend

모델 계층의 기본 무결성(외래키, 유니크 제약, 기본 타임스탬프)을 보강한 상태입니다.

## Quick Start

```powershell
python -m pip install -r req.txt
python -m pytest -q
```

## What Was Improved

- 모델 import 경로를 `src.*`로 통일
- 잘못된 직접 참조 FK를 문자열 FK로 전환해 순환 import 리스크 완화
- `Vote`에 `option_id`를 추가해 어떤 선택지에 투표했는지 저장 가능
- 중복 투표/옵션 순서 충돌 방지용 유니크 제약 추가
- `created_at` 기본값(`CURRENT_TIMESTAMP`) 적용
- `DATABASE_URL` 미설정 시에도 로컬 SQLite로 실행 가능

