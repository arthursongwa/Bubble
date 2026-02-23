from datetime import datetime
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except:
        pass


def get_clock() -> dict:
    now = datetime.now()
    try:
        date_str = now.strftime("%A %d %B %Y").capitalize()
    except:
        date_str = now.strftime("%Y-%m-%d")

    return {
        "time": now.strftime("%H:%M:%S"),
        "date": date_str,
        "week": f"SEMAINE {now.strftime('%W').zfill(2)}",
        "ts":   now.isoformat(),
    }