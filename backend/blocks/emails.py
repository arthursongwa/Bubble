import imaplib
import email
from email.header import decode_header
from datetime import datetime, timezone
import os
import re


def _decode(value, default=""):
    if not value:
        return default
    parts = decode_header(value)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result).strip()


def _relative_date(date_str: str) -> str:
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 3600:
            m = int(seconds // 60)
            return f"Il y a {m}min" if m > 1 else "À l'instant"
        elif seconds < 86400:
            h = int(seconds // 3600)
            return f"Il y a {h}h"
        elif seconds < 172800:
            return "Hier"
        else:
            d = int(seconds // 86400)
            return f"Il y a {d}j"
    except:
        return date_str or ""


def _extract_name(from_str: str) -> str:
    """Extrait juste le nom (pas l'email)."""
    if not from_str:
        return "Inconnu"
    match = re.match(r'^"?([^"<]+)"?\s*<', from_str)
    if match:
        return match.group(1).strip().strip('"')
    match = re.match(r'([^@<\s]+)', from_str)
    return match.group(1) if match else from_str.split("@")[0]


def get_emails() -> dict:
    host     = os.environ.get("EMAIL_HOST", "imap.gmail.com")
    email_   = os.environ.get("EMAIL_ADDRESS", "")
    password = os.environ.get("EMAIL_PASSWORD", "")
    max_n    = int(os.environ.get("EMAIL_MAX", "6"))

    if not email_ or not password:
        return {"error": "EMAIL_ADDRESS et EMAIL_PASSWORD non configurés", "emails": [], "total": 0}

    try:
        mail = imaplib.IMAP4_SSL(host)
        mail.login(email_, password)
        mail.select("INBOX")

        _, data = mail.search(None, "UNSEEN")
        ids = data[0].split()
        total = len(ids)

        # Prend les N plus récents
        recent_ids = ids[-max_n:] if len(ids) > max_n else ids
        recent_ids = list(reversed(recent_ids))

        emails = []
        for uid in recent_ids:
            _, msg_data = mail.fetch(uid, "(RFC822.HEADER)")
            if not msg_data or not msg_data[0]:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            emails.append({
                "from":    _extract_name(_decode(msg.get("From", ""))),
                "subject": _decode(msg.get("Subject", "(sans objet)")),
                "date":    _relative_date(msg.get("Date", "")),
                "unread":  True,
            })

        mail.logout()
        return {"emails": emails, "total": total, "error": None}

    except imaplib.IMAP4.error as e:
        return {"error": f"Authentification échouée : {e}", "emails": [], "total": 0}
    except Exception as e:
        return {"error": str(e), "emails": [], "total": 0}