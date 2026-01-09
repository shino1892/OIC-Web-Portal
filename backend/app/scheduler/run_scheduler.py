from __future__ import annotations

import os
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from app.utility.timetable_sync.sync_service import sync_all_departments


def main():
    tz = os.environ.get("TZ", "Asia/Tokyo")
    scheduler = BlockingScheduler(timezone=tz)

    # Every day at 06:00 and 18:00
    scheduler.add_job(sync_all_departments, "cron", hour=6, minute=0, id="timetable_sync_morning")
    scheduler.add_job(sync_all_departments, "cron", hour=18, minute=0, id="timetable_sync_evening")

    print("[scheduler] started (06:00/18:00)", flush=True)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    # Small delay to allow DB container to be ready in compose
    time.sleep(3)
    main()
