from __future__ import annotations

import os
import pickle
import traceback
from dataclasses import dataclass
from datetime import datetime

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from app.utility.db.db_connect import db_connect
from app.utility.db.db_notifications import create_notification
from app.utility.db.db_sync_config import (
    list_enabled_department_spreadsheets,
    resolve_class_id,
    resolve_major_id_by_alias,
)
from app.utility.db.db_sync_runs import get_last_success_at, upsert_sync_run
from app.utility.timetable_sync.sheet_extract import (
    find_block_headers,
    normalize_text,
    parse_block_map,
)


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _authorize_custom(flow: InstalledAppFlow):
    flow.redirect_uri = "http://localhost:8080/"
    auth_url, _ = flow.authorization_url(prompt="consent")
    print(f"Please visit this URL to authorize: {auth_url}")
    code = input("Enter the authorization code: ")
    flow.fetch_token(code=code)
    return flow.credentials


def get_gspread_client(credentials_file: str, token_file: str):
    creds = None

    if os.path.exists(token_file):
        try:
            with open(token_file, "rb") as token:
                creds = pickle.load(token)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = _authorize_custom(flow)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)


def get_or_create_subject(conn, subject_name: str):
    subject_name = normalize_text(subject_name)
    if not subject_name or subject_name == "-":
        return None

    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM subjects WHERE name = %s", (subject_name,))
        r = cursor.fetchone()
        if r:
            return r["id"]
        cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (subject_name,))
        return cursor.lastrowid


def get_or_create_teacher(conn, teacher_name: str):
    teacher_name = normalize_text(teacher_name)
    if not teacher_name or teacher_name in ("-", "None"):
        teacher_name = "未定"

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM teacher_users WHERE full_name = %s", (teacher_name,))
        r = cursor.fetchone()
        if r:
            return r["user_id"]

        cursor.execute(
            "SELECT MAX(user_id) as max_id FROM teacher_users WHERE user_id >= 100000 AND user_id < 200000"
        )
        row = cursor.fetchone()
        max_id = row["max_id"] if row and row.get("max_id") else 99999
        new_id = int(max_id) + 1

        email = f"teacher_{new_id}@generated.local"
        cursor.execute(
            "INSERT INTO teacher_users (user_id, full_name, email) VALUES (%s, %s, %s)",
            (new_id, teacher_name, email),
        )
        return new_id


@dataclass(frozen=True)
class TimetableRow:
    class_id: int
    major_id: int | None
    date: str  # YYYY-MM-DD
    period: int
    subject_name: str
    teacher_name: str


def _compute_specific_subjects(per_major_subjects: dict[tuple[str, int], dict[str, str | None]]):
    specific = set()
    for _, subjects_by_major in per_major_subjects.items():
        subjects = {s for s in subjects_by_major.values() if s}
        if len(subjects) >= 2:
            specific.update(subjects)
    return specific


def _merge_major_blocks(
    *,
    grade: int,
    class_id: int,
    majors: list[str],
    subj_maps: dict[str, dict[tuple[str, int], str]],
    teacher_maps: dict[str, dict[tuple[str, int], str]],
    department_id: int,
):
    """Return list[TimetableRow] for this grade.

    majors: list of major_alias strings (no None). If empty => no-major mode.
    """
    if not majors:
        # no-major mode: pick the first maps by any key
        # We assume there is a single block (major_alias None)
        only_key = next(iter(subj_maps.keys()))
        s_map = subj_maps[only_key]
        t_map = teacher_maps.get(only_key, {})
        keys = set(s_map.keys()) | set(t_map.keys())
        out: list[TimetableRow] = []
        for (date, period) in keys:
            subj = normalize_text(s_map.get((date, period), ""))
            teach = normalize_text(t_map.get((date, period), ""))
            if subj == "-":
                subj = ""
            if teach in ("-", "None"):
                teach = ""
            if subj and not teach:
                teach = "未定"
            if teach and not subj:
                # keep teacher-only rows out
                continue
            if not subj:
                continue
            out.append(
                TimetableRow(
                    class_id=class_id,
                    major_id=None,
                    date=date,
                    period=period,
                    subject_name=subj,
                    teacher_name=teach or "未定",
                )
            )
        return out

    # Build per slot dictionaries
    all_keys: set[tuple[str, int]] = set()
    for m in majors:
        all_keys |= set(subj_maps.get(m, {}).keys())
        all_keys |= set(teacher_maps.get(m, {}).keys())

    # Normalize and fill missing subjects when teacher exists
    per_major_subjects: dict[tuple[str, int], dict[str, str | None]] = {}
    per_major_teachers: dict[tuple[str, int], dict[str, str | None]] = {}

    for key in all_keys:
        per_major_subjects[key] = {}
        per_major_teachers[key] = {}
        for m in majors:
            s = normalize_text(subj_maps.get(m, {}).get(key, ""))
            t = normalize_text(teacher_maps.get(m, {}).get(key, ""))
            if s == "-":
                s = ""
            if t in ("-", "None"):
                t = ""
            per_major_subjects[key][m] = s or None
            per_major_teachers[key][m] = t or None

    # fill missing subject if teacher exists using any other major subject
    for key in all_keys:
        any_subject = next((s for s in per_major_subjects[key].values() if s), None)
        for m in majors:
            if per_major_teachers[key][m] and not per_major_subjects[key][m]:
                per_major_subjects[key][m] = any_subject

    # missing teacher but subject exists -> 未定
    for key in all_keys:
        for m in majors:
            if per_major_subjects[key][m] and not per_major_teachers[key][m]:
                per_major_teachers[key][m] = "未定"

    specific_subjects = _compute_specific_subjects(per_major_subjects)

    out: list[TimetableRow] = []
    for (date, period) in all_keys:
        majors_with_class = [m for m in majors if per_major_subjects[(date, period)].get(m)]
        if not majors_with_class:
            continue

        subjects = {per_major_subjects[(date, period)][m] for m in majors_with_class}
        teachers = {per_major_teachers[(date, period)][m] for m in majors_with_class}

        is_common = False
        if len(subjects) == 1 and len(teachers) == 1:
            is_common = True
        elif len(majors_with_class) == 1:
            only_m = majors_with_class[0]
            only_subject = per_major_subjects[(date, period)][only_m]
            if only_subject and only_subject not in specific_subjects:
                is_common = True

        if is_common:
            pick_m = majors_with_class[0]
            subj = per_major_subjects[(date, period)][pick_m] or ""
            teach = per_major_teachers[(date, period)][pick_m] or "未定"
            out.append(
                TimetableRow(
                    class_id=class_id,
                    major_id=None,
                    date=date,
                    period=period,
                    subject_name=subj,
                    teacher_name=teach,
                )
            )
            continue

        for m in majors_with_class:
            subj = per_major_subjects[(date, period)][m]
            teach = per_major_teachers[(date, period)][m]
            if not subj:
                continue
            major_id = resolve_major_id_by_alias(department_id, m)
            if major_id is None:
                print(f"[WARN] department {department_id} grade {grade}: major alias '{m}' unresolved; treating as common")
            out.append(
                TimetableRow(
                    class_id=class_id,
                    major_id=major_id,
                    date=date,
                    period=period,
                    subject_name=subj,
                    teacher_name=teach or "未定",
                )
            )

    return out


def _fetch_existing(conn, class_id: int, min_date: str, max_date: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT t.major_id, t.date, t.period, s.name AS subject_name, u.full_name AS teacher_name
            FROM timetables t
            LEFT JOIN subjects s ON t.subject_id = s.id
            LEFT JOIN teacher_users u ON t.teacher_id = u.user_id
            WHERE t.class_id = %s AND t.date BETWEEN %s AND %s
            """,
            (class_id, min_date, max_date),
        )
        rows = cursor.fetchall()

    out = {}
    for r in rows:
        key = (r["major_id"], r["date"].strftime("%Y-%m-%d"), int(r["period"]))
        out[key] = (normalize_text(r.get("subject_name") or ""), normalize_text(r.get("teacher_name") or ""))
    return out


def _diff(old_map, new_map):
    added = []
    removed = []
    changed = []

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    for k in new_keys - old_keys:
        added.append((k, new_map[k]))
    for k in old_keys - new_keys:
        removed.append((k, old_map[k]))
    for k in new_keys & old_keys:
        if old_map[k] != new_map[k]:
            changed.append((k, old_map[k], new_map[k]))

    return added, removed, changed


def _create_change_notifications(class_id: int, department_id: int, added, removed, changed):
    # Create per-slot notifications; scope=CLASS, major_id is embedded in key
    for (major_id, date, period), (subj, teach) in added:
        msg = f"{date} {period}限: 追加 {subj}（{teach}）"
        create_notification(
            notif_type="授業変更",
            message=msg,
            scope="CLASS",
            department_id=department_id,
            class_id=class_id,
            major_id=major_id,
        )

    for (major_id, date, period), (subj, teach) in removed:
        msg = f"{date} {period}限: 削除 {subj}（{teach}）"
        create_notification(
            notif_type="授業変更",
            message=msg,
            scope="CLASS",
            department_id=department_id,
            class_id=class_id,
            major_id=major_id,
        )

    for (major_id, date, period), (old_subj, old_teach), (new_subj, new_teach) in changed:
        msg = f"{date} {period}限: 変更 {old_subj}（{old_teach}）→ {new_subj}（{new_teach}）"
        create_notification(
            notif_type="授業変更",
            message=msg,
            scope="CLASS",
            department_id=department_id,
            class_id=class_id,
            major_id=major_id,
        )


def sync_one_department(
    *,
    client,
    department_id: int,
    spreadsheet_id: str,
    worksheet_name: str,
    credentials_file: str,
    token_file: str,
):
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    data = sheet.get_all_values()

    # 初回成功までは通知を抑制（初回同期は差分が膨大になりがち）
    had_success_before = get_last_success_at(department_id) is not None
    upsert_sync_run(department_id=department_id, status="running", error_message=None, mark_success=False)

    headers = find_block_headers(data)

    # Organize by grade
    by_grade: dict[int, dict[str | None, dict[str, int]]] = {}
    # We'll store header row index per (grade, major_alias, type)
    for h in headers:
        by_grade.setdefault(h.grade, {}).setdefault(h.major_alias, {})[h.block_type] = h.row_index

    final_rows: list[TimetableRow] = []

    for grade, majors_dict in sorted(by_grade.items()):
        class_id = resolve_class_id(department_id, grade)
        if not class_id:
            print(f"[WARN] department {department_id} grade {grade}: class not found; skipping")
            continue

        def _is_effectively_empty(value: str | None) -> bool:
            v = normalize_text(value or "")
            return (not v) or v == "-"

        common_subj_map: dict[tuple[str, int], str] = {}
        common_teach_map: dict[tuple[str, int], str] = {}
        if None in majors_dict:
            idxs_common = majors_dict.get(None) or {}
            common_subj_idx = idxs_common.get("subject")
            common_teach_idx = idxs_common.get("teacher")
            if common_subj_idx is not None:
                common_subj_map = parse_block_map(data, common_subj_idx)
                common_teach_map = (
                    parse_block_map(data, common_teach_idx) if common_teach_idx is not None else {}
                )

        # majors can be None (no-major) or strings
        if set(majors_dict.keys()) == {None}:
            idxs = majors_dict[None]
            subj_idx = idxs.get("subject")
            teach_idx = idxs.get("teacher")
            if subj_idx is None:
                continue
            subj_map = parse_block_map(data, subj_idx)
            teach_map = parse_block_map(data, teach_idx) if teach_idx is not None else {}

            # Use a sentinel key for no-major mode
            merged = _merge_major_blocks(
                grade=grade,
                class_id=class_id,
                majors=[],
                subj_maps={"__NO_MAJOR__": subj_map},
                teacher_maps={"__NO_MAJOR__": teach_map},
                department_id=department_id,
            )
            final_rows.extend(merged)
            continue

        # majors exist: parse each major that has a subject block
        majors: list[str] = []
        subj_maps: dict[str, dict[tuple[str, int], str]] = {}
        teacher_maps: dict[str, dict[tuple[str, int], str]] = {}

        for major_alias, idxs in majors_dict.items():
            if major_alias is None:
                continue
            subj_idx = idxs.get("subject")
            teach_idx = idxs.get("teacher")
            if subj_idx is None:
                continue
            majors.append(major_alias)
            subj_maps[major_alias] = parse_block_map(data, subj_idx)
            teacher_maps[major_alias] = parse_block_map(data, teach_idx) if teach_idx is not None else {}

        # If a common (no-major) block exists for this grade, treat it as the base timetable.
        # We merge common cells into each major only when that major cell is missing/blank.
        # This avoids creating duplicate rows at query-time (get_timetable selects both major_id and NULL).
        if common_subj_map and majors:
            for m in majors:
                s_map = subj_maps.get(m) or {}
                t_map = teacher_maps.get(m) or {}

                for key, value in common_subj_map.items():
                    if key not in s_map or _is_effectively_empty(s_map.get(key)):
                        s_map[key] = value
                for key, value in common_teach_map.items():
                    if key not in t_map or _is_effectively_empty(t_map.get(key)):
                        t_map[key] = value

                subj_maps[m] = s_map
                teacher_maps[m] = t_map

        # If we didn't find any per-major subject blocks but we do have a common block, fall back to no-major.
        if not majors and common_subj_map:
            merged = _merge_major_blocks(
                grade=grade,
                class_id=class_id,
                majors=[],
                subj_maps={"__NO_MAJOR__": common_subj_map},
                teacher_maps={"__NO_MAJOR__": common_teach_map},
                department_id=department_id,
            )
            final_rows.extend(merged)
            continue

        if not majors:
            # Nothing to sync for this grade.
            continue

        merged = _merge_major_blocks(
            grade=grade,
            class_id=class_id,
            majors=majors,
            subj_maps=subj_maps,
            teacher_maps=teacher_maps,
            department_id=department_id,
        )
        final_rows.extend(merged)

    if not final_rows:
        print(f"[INFO] department {department_id}: no timetable rows parsed")
        return

    # Determine date range per class_id and apply changes
    conn = db_connect()
    if not conn:
        print("Failed to connect to DB")
        return

    try:
        # Group by class_id for diff and replace
        by_class: dict[int, list[TimetableRow]] = {}
        for r in final_rows:
            by_class.setdefault(r.class_id, []).append(r)

        with conn.cursor() as cursor:
            for class_id, rows in by_class.items():
                dates = [rr.date for rr in rows]
                min_date = min(dates)
                max_date = max(dates)

                old_map = _fetch_existing(conn, class_id, min_date, max_date)

                new_map = {}
                for rr in rows:
                    key = (rr.major_id, rr.date, rr.period)
                    new_map[key] = (normalize_text(rr.subject_name), normalize_text(rr.teacher_name))

                added, removed, changed = _diff(old_map, new_map)

                if had_success_before and (added or removed or changed):
                    _create_change_notifications(class_id, department_id, added, removed, changed)

                # Replace the range for this class
                cursor.execute(
                    "DELETE FROM timetables WHERE class_id = %s AND date BETWEEN %s AND %s",
                    (class_id, min_date, max_date),
                )

                for rr in rows:
                    subj_id = get_or_create_subject(conn, rr.subject_name)
                    teach_id = get_or_create_teacher(conn, rr.teacher_name)
                    cursor.execute(
                        """
                        INSERT INTO timetables (class_id, major_id, date, period, subject_id, teacher_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (rr.class_id, rr.major_id, rr.date, rr.period, subj_id, teach_id),
                    )

        conn.commit()
        print(f"[OK] department {department_id}: synced ({len(final_rows)} rows)")
        upsert_sync_run(department_id=department_id, status="success", error_message=None, mark_success=True)

    except Exception as e:
        print(f"sync_one_department error: {e}")
        traceback.print_exc()
        upsert_sync_run(
            department_id=department_id,
            status="failed",
            error_message=str(e),
            mark_success=False,
        )
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()


def sync_all_departments():
    # Use debug credentials by default (per requirement)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    debug_dir = os.path.join(base_dir, "debug")

    credentials_file = os.environ.get(
        "TIMETABLE_SYNC_CREDENTIALS_FILE", os.path.join(debug_dir, "credentials.json")
    )
    token_file = os.environ.get("TIMETABLE_SYNC_TOKEN_FILE", os.path.join(debug_dir, "token.pickle"))

    client = get_gspread_client(credentials_file, token_file)

    for row in list_enabled_department_spreadsheets():
        department_id = int(row["department_id"])
        spreadsheet_id = row["spreadsheet_id"]
        worksheet_name = row["worksheet_name"]
        print(f"[INFO] syncing department {department_id} ({worksheet_name})")
        sync_one_department(
            client=client,
            department_id=department_id,
            spreadsheet_id=spreadsheet_id,
            worksheet_name=worksheet_name,
            credentials_file=credentials_file,
            token_file=token_file,
        )
