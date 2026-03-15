# ComicLog

ComicLog는 읽은 만화를 기록하는 모바일 앱의 초기 프로젝트입니다.

## 프로젝트 구조

```text
comiclog/
  main.py
  db/
    database.py
  models/
  services/
  ui/
    home_screen.py
  database/
```

## 데이터베이스 설계

`comiclog/db/database.py`에서 아래 테이블을 생성합니다.

- `works`: 작품 기본 정보
- `episodes`: 읽은 화(작품별 에피소드) 기록
- `memos`: 감상 메모 + 명장면
- `tags`: 태그 마스터
- `memo_tags`: 메모-태그 다대다 관계

Foreign Key 관계:
- `episodes.work_id -> works.id`
- `memos.episode_id -> episodes.id`
- `memo_tags.memo_id -> memos.id`
- `memo_tags.tag_id -> tags.id`

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m comiclog.main
```
