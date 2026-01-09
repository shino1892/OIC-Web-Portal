from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    return unicodedata.normalize("NFKC", str(text)).strip()


_date_re = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")


def parse_dates_from_row(row: list[str], start_col: int = 1) -> dict[int, str]:
    """Return {col_index: 'YYYY-MM-DD'} for date cells."""
    out: dict[int, str] = {}
    for col_idx in range(start_col, len(row)):
        cell = normalize_text(row[col_idx])
        m = _date_re.search(cell)
        if not m:
            continue
        y, mo, d = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime(int(y), int(mo), int(d)).date()
        except ValueError:
            continue
        out[col_idx] = dt.strftime("%Y-%m-%d")
    return out


_period_re = re.compile(r"^(?P<p>[1-9])\s*コマ目")


def iter_period_rows(data: list[list[str]], start_row: int, max_period: int = 7):
    """Yield (period, row_index, row_data) scanning downward starting at start_row."""
    for r in range(start_row, min(len(data), start_row + 40)):
        row = data[r]
        head = normalize_text(row[0]) if row else ""
        if not head:
            # allow a couple empty lines but stop if we've already started
            continue
        m = _period_re.match(head)
        if not m:
            # hit next section
            break
        period = int(m.group("p"))
        if period < 1 or period > max_period:
            continue
        yield period, r, row


@dataclass(frozen=True)
class BlockHeader:
    row_index: int
    grade: int
    major_alias: str | None
    block_type: str  # 'subject' | 'teacher'


_grade_re = re.compile(r"(?P<g>[1-9])\s*年")


def extract_major_alias(header_text: str) -> str | None:
    """Extract something like 'SC専攻' or 'AI・IoT専攻' if present."""
    if "専攻" not in header_text:
        return None

    # Try to capture the last '<something>専攻' segment
    m = re.search(r"([\wぁ-んァ-ヶ一-龠A-Za-z0-9・\-]+専攻)", header_text)
    if not m:
        return None
    return m.group(1)


def find_block_headers(data: list[list[str]]) -> list[BlockHeader]:
    headers: list[BlockHeader] = []
    for i, row in enumerate(data):
        if not row:
            continue
        head = normalize_text(row[0])
        if not head:
            continue

        gm = _grade_re.search(head)
        if not gm:
            continue
        grade = int(gm.group("g"))

        if i + 1 >= len(data) or not data[i + 1]:
            continue
        next_head = normalize_text(data[i + 1][0])

        block_type = None
        if "時間割" in next_head:
            block_type = "subject"
        elif "担当" in next_head:
            block_type = "teacher"
        else:
            continue

        headers.append(
            BlockHeader(
                row_index=i,
                grade=grade,
                major_alias=extract_major_alias(head),
                block_type=block_type,
            )
        )

    return headers


def parse_block_map(
    data: list[list[str]],
    header_row_index: int,
) -> dict[tuple[str, int], str]:
    """Parse a subject/teacher block into {(date_str, period): value}.

    Expects:
    - date row at header_row_index + 1
    - period rows starting at header_row_index + 2
    """
    date_row = data[header_row_index + 1]
    date_map = parse_dates_from_row([normalize_text(c) for c in date_row])

    out: dict[tuple[str, int], str] = {}
    for period, _, row in iter_period_rows(data, header_row_index + 2):
        for col_idx, date_str in date_map.items():
            if col_idx >= len(row):
                continue
            cell = normalize_text(row[col_idx])
            if not cell:
                continue
            out[(date_str, period)] = cell
    return out
