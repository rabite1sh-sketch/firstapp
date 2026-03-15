from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from comiclog.db.database import DEFAULT_DB_PATH, connect_db


class StatsService:
    """ComicLog 통계 데이터를 집계하고 시각화 파일을 생성하는 서비스."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH, artifact_dir: str = "comiclog/database/stats") -> None:
        """DB 경로와 통계 산출물(이미지) 저장 폴더를 설정합니다."""
        self._db_path = db_path
        self._artifact_dir = Path(artifact_dir)
        self._artifact_dir.mkdir(parents=True, exist_ok=True)

    def get_summary(self) -> dict[str, Any]:
        """요구된 핵심 통계(총 읽은 화, 메모 수, 작품별 기록)를 반환합니다."""
        with connect_db(self._db_path) as conn:
            total_episodes = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            total_memos = conn.execute("SELECT COUNT(*) FROM memos").fetchone()[0]
            per_work_rows = conn.execute(
                """
                SELECT w.title AS work_title, COUNT(e.id) AS episode_count
                FROM works w
                LEFT JOIN episodes e ON e.work_id = w.id
                GROUP BY w.id, w.title
                ORDER BY episode_count DESC, w.title ASC
                """
            ).fetchall()

        per_work = [
            {"work_title": row["work_title"], "episode_count": row["episode_count"]}
            for row in per_work_rows
        ]

        return {
            "total_read_episodes": int(total_episodes),
            "memo_count": int(total_memos),
            "records_by_work": per_work,
        }

    def generate_episode_bar_chart(self, filename: str = "episodes_by_work.png") -> str | None:
        """작품별 읽은 화 수를 막대 차트 이미지로 생성하고 경로를 반환합니다.

        Returns:
            이미지 파일 경로. `matplotlib`가 없거나 데이터가 없으면 `None`.
        """
        try:
            import matplotlib.pyplot as plt
        except Exception:
            return None

        summary = self.get_summary()
        records = summary["records_by_work"]
        if not records:
            return None

        titles = [r["work_title"] for r in records]
        counts = [r["episode_count"] for r in records]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(titles, counts)
        ax.set_title("작품별 읽은 화 수")
        ax.set_xlabel("작품")
        ax.set_ylabel("읽은 화")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()

        output = self._artifact_dir / filename
        fig.savefig(output)
        plt.close(fig)
        return str(output)

    def generate_memo_wordcloud(self, filename: str = "memo_wordcloud.png") -> str | None:
        """메모 텍스트 기반 워드클라우드 이미지를 생성하고 경로를 반환합니다.

        Returns:
            이미지 파일 경로. `wordcloud`가 없거나 메모 텍스트가 없으면 `None`.
        """
        try:
            from wordcloud import WordCloud
        except Exception:
            return None

        with connect_db(self._db_path) as conn:
            rows = conn.execute("SELECT memo_text FROM memos").fetchall()

        text = " ".join((row["memo_text"] or "").strip() for row in rows).strip()
        if not text:
            return None

        # 기본 폰트 설정(환경 차이를 고려해 시스템 기본으로 시도)
        wc = WordCloud(width=1000, height=500, background_color="white")
        image = wc.generate(text)

        output = self._artifact_dir / filename
        image.to_file(str(output))
        return str(output)

    def get_top_words(self, limit: int = 20) -> list[tuple[str, int]]:
        """간단한 토큰 빈도 기반 상위 단어를 반환합니다."""
        with connect_db(self._db_path) as conn:
            rows = conn.execute("SELECT memo_text FROM memos").fetchall()

        counter: Counter[str] = Counter()
        for row in rows:
            text = (row["memo_text"] or "").strip()
            if not text:
                continue
            for token in text.replace("\n", " ").split(" "):
                token = token.strip(" ,.!?()[]{}\"'\t")
                if len(token) >= 2:
                    counter[token] += 1

        return counter.most_common(limit)
