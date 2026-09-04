"""Temporarily list active TimeTree calendar names and alias codes.

This diagnostic intentionally does not fetch events or initialize Google
Calendar.  It prints only the two fields needed to identify a calendar.
"""

import logging
import os

from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# The vendor client may include raw server responses in error logs.  Keep its
# logs silent so credentials, cookies, session IDs, and unexpected API payloads
# can never reach the GitHub Actions log.
logging.getLogger("timetree_exporter").setLevel(logging.CRITICAL + 1)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def main() -> None:
    email = _required_env("TIMETREE_EMAIL")
    password = _required_env("TIMETREE_PASSWORD")

    session_id = login(email, password)
    if session_id is None:
        raise RuntimeError("TimeTree login did not return a session.")

    calendars = TimeTreeCalendar(session_id).get_metadata()
    for calendar in calendars:
        if calendar.get("deactivated_at") is not None:
            continue

        name = str(calendar.get("name") or "Unnamed")
        alias_code = str(calendar.get("alias_code") or "")
        logger.info("name=%r alias_code=%r", name, alias_code)


if __name__ == "__main__":
    main()
