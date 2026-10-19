"""Scrape the public contributions calendar into data/contributions.json (no token needed)."""

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "CadPosting"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse_count(text: str) -> int:
    """Tooltip text looks like 'No contributions on ...' or '3 contributions on ...'."""
    match = re.match(r"\s*([\d,]+)\s+contribution", text)
    return int(match.group(1).replace(",", "")) if match else 0


def main() -> None:
    url = f"https://github.com/users/{USERNAME}/contributions"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # LEARN: counts live in <tool-tip for="cell-id">, not on the <td> itself
    counts = {tip.get("for"): parse_count(tip.get_text()) for tip in soup.find_all("tool-tip")}

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append(
            {
                "date": td["data-date"],
                "level": int(td.get("data-level", 0)),
                "count": counts.get(td.get("id"), 0),
            }
        )
    if not days:
        raise SystemExit("No contribution cells found; GitHub markup may have changed.")

    days.sort(key=lambda d: d["date"])
    data = {"username": USERNAME, "total": sum(d["count"] for d in days), "days": days}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"{len(days)} days, {data['total']} contributions -> {OUT}")


if __name__ == "__main__":
    main()
