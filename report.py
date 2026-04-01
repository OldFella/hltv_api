import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from itertools import zip_longest
from ua_parser import user_agent_parser
from user_agents import parse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

LOG_PATH  = Path("./logs/nginx/access.log")
COL_WIDTH = 45

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) \d+ '
    r'"[^"]*" "(?P<ua>[^"]*)" "[^"]*" "(?P<host>[^"]*)"'
)

BOT_KEYWORDS = {
    "bot", "crawler", "spider", "deno", "supabase", "curl", "python",
    "wget", "paloalto", "xpanse", "zgrab", "libredtail", "ahrefs",
    "censysinspect", "go-http-client", "alittle client", "chrome privacy prefetch proxy"
}

IGNORED_PREFIXES = {"/static", "/favicon"}

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def get_device(ua: str) -> str:
    ua_str = ua.strip()
    if ua_str in ("", "-") or ua_str == "Mozilla/5.0":
        return "Bot"
    if any(k in ua_str.lower() for k in BOT_KEYWORDS):
        return "Bot"

    if "networkingextension" in ua_str and "ios" in ua_str:
        return "Bot"
    parsed = parse(ua_str)

    if parsed.is_pc:
        os_name = parsed.os[0]  # e.g., 'Windows', 'Mac OS X'
        return f"Desktop ({os_name})"

    if parsed.is_mobile:
        os_name = parsed.os[0]  # e.g., 'Windows', 'Mac OS X'
        return f"Smartphone ({os_name})"
    if parsed.is_tablet:
        os_name = parsed.os[0]  # e.g., 'Windows', 'Mac OS X'
        return f"Tablet ({os_name})"

    # fallback
    return "Bot"

def parse_log(path: Path) -> list[dict]:
    entries = []
    for line in path.read_text().splitlines():
        m = LOG_PATTERN.match(line)
        if not m:
            continue
        path_str = m["path"].split("?")[0]
        if any(path_str.startswith(p) for p in IGNORED_PREFIXES):
            continue
        dt = datetime.strptime(m["time"], "%d/%b/%Y:%H:%M:%S %z")
        ua = m["ua"]
        entries.append({
            "ip":     m["ip"],
            "time":   dt,
            "method": m["method"],
            "path":   path_str,
            "status": int(m["status"]),
            "ua":     ua,
            "host":   m["host"],
            "is_bot": any(k in ua.lower() for k in BOT_KEYWORDS),
            "device": get_device(ua),
        })
    return entries

# ---------------------------------------------------------------------------
# Section builder
# ---------------------------------------------------------------------------

def build_section(entries: list[dict]) -> list[str]:
    if not entries:
        return ["  (no data)"]

    unique_subnets   = defaultdict(set)
    requests_per_day = defaultdict(int)
    endpoint_counts  = defaultdict(int)
    status_counts    = defaultdict(int)
    hour_counts      = defaultdict(int)
    device_counts    = defaultdict(int)
    bot_requests     = 0
    browser_requests = 0

    for e in entries:
        day = e["time"].date()
        unique_subnets[day].add(e["ip"])
        requests_per_day[day] += 1
        endpoint_counts[e["path"]] += 1
        status_counts[e["status"]] += 1
        hour_counts[e["time"].hour] += 1
        device_counts[e["device"]] += 1
        if e["is_bot"]:
            bot_requests += 1
        else:
            browser_requests += 1

    total = len(entries)
    w     = COL_WIDTH - 2
    div   = "-" * w
    lines = []

    def h(title):
        lines.append(f"  {title}")
        lines.append(f"  {div}")

    # Traffic per day
    h("TRAFFIC PER DAY")
    for day in sorted(unique_subnets):
        lines.append(f"  {day}  {requests_per_day[day]:>5} reqs  {len(unique_subnets[day]):>3} subnets")

    # Endpoints
    lines.append("")
    h("TOP ENDPOINTS")
    for path, count in sorted(endpoint_counts.items(), key=lambda x: -x[1])[:10]:
        lines.append(f"  {path:<28} {count:>4}")

    # Status codes
    lines.append("")
    h("STATUS CODES")
    for status, count in sorted(status_counts.items()):
        pct = count / total * 100
        lines.append(f"  {status}  {count:>4} ({pct:>5.1f}%)")

    # Bot vs browser
    lines.append("")
    h("BOT vs BROWSER")
    lines.append(f"  Browser  {browser_requests:>4} ({browser_requests / total * 100:>5.1f}%)")
    lines.append(f"  Bot      {bot_requests:>4} ({bot_requests / total * 100:>5.1f}%)")

    # Devices
    lines.append("")
    h("DEVICES")
    for device, count in sorted(device_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        lines.append(f"  {device:<28} {count:>4} ({pct:>5.1f}%)")

    # Busiest hours
    lines.append("")
    h("BUSIEST HOURS (UTC)")
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        lines.append(f"  {hour:02d}:00  {count:>4}")

    lines.append("")
    lines.append(f"  TOTAL: {total} requests")

    return lines

# ---------------------------------------------------------------------------
# Side-by-side printer
# ---------------------------------------------------------------------------

def print_side_by_side(left_title: str, left: list[str],
                       right_title: str, right: list[str]) -> None:
    w   = COL_WIDTH
    sep = "  │  "

    print("═" * w + "══╪══" + "═" * w)
    print(f"{left_title:^{w}}{sep}{right_title:^{w}}")
    print("═" * w + "══╪══" + "═" * w)

    for l, r in zip_longest(left, right, fillvalue=""):
        print(f"{l:<{w}}{sep}{r}")

    print("═" * w + "══╧══" + "═" * w)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    entries  = parse_log(LOG_PATH)

    # cutoff  = datetime.now(tz=timezone.utc) - timedelta(hours=24)
    # entries = [e for e in entries if e["time"] >= cutoff]

    frontend = [e for e in entries if "www.csapi.de" in e["host"]]
    backend  = [e for e in entries if "api.csapi.de" in e["host"]]

    print_side_by_side(
        "FRONTEND  (www.csapi.de)", build_section(frontend),
        "BACKEND   (api.csapi.de)", build_section(backend)
    )
