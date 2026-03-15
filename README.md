# ComicLog

ComicLog는 읽은 만화를 기록하고, 감상 메모/명장면/통계를 관리하는 Python + Flet + SQLite 기반 모바일 앱입니다.

## 기술 스택
- Python 3.10+
- Flet
- SQLite

## 프로젝트 구조

```text
comiclog/
  main.py                     # 앱 진입점 + NavigationBar 탭/라우트 제어
  db/
    database.py               # DB 연결/스키마 생성/초기화
  models/
    comic_entry.py            # 예시 도메인 모델
  services/
    work_service.py           # 작품 CRUD
    memo_service.py           # 메모 CRUD
    highlight_service.py      # 명장면 조회 서비스
    stats_service.py          # 통계/차트/워드클라우드
  ui/
    home_view.py              # Home 탭(소개 + 최근 활동)
    work_list_view.py         # Works 탭(작품 목록)
    work_detail_view.py       # 작품 상세
    highlight_view.py         # Highlights 탭
    stats_view.py             # Stats 탭
```

## 화면 구성 (모바일 UX)

하단 `NavigationBar` 탭:
- Home: 앱 소개와 최근 활동
- Works: 작품 목록/추가/상세
- Highlights: 명장면 모음
- Stats: 읽은 화 수/메모 수/작품별 기록 + 시각화

`main.py`에서 탭 선택과 route(` /, /works, /works/new, /works/{id}, /highlights, /stats`)를 함께 관리합니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m comiclog.main
```

## 파일 역할 상세

- `db/database.py`
  - `connect_db()`: SQLite 연결 + Foreign Key 활성화
  - `create_tables()`: works/episodes/memos/tags/memo_tags 테이블 생성
  - `initialize_db()`: DB 최초 초기화 실행
- `services/work_service.py`
  - 작품 등록/조회/수정/삭제 담당
- `services/memo_service.py`
  - 에피소드 메모 등록/조회/수정/삭제 담당
- `services/highlight_service.py`
  - 명장면 필터링 및 작품별 그룹 조회 담당
- `services/stats_service.py`
  - 총 읽은 화, 메모 수, 작품별 기록 집계
  - matplotlib 차트 + QuickChart 워드클라우드 URL 생성
- `ui/*_view.py`
  - 각 탭/화면을 독립 뷰로 분리해 확장 가능한 구조 유지
