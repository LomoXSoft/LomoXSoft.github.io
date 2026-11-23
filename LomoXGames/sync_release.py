"""Synchronizes LomoXGames/matritellus_release.json with the latest version in Matritellus README.md (or GitHub release).

Usage:
    python dist/_lomoxsoft_site/LomoXGames/sync_release.py [--push]
"""
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.dirname(HERE)
WORKSPACE = os.path.dirname(os.path.dirname(SITE_ROOT))
README_PATH = os.path.join(WORKSPACE, "README.md")
OUT_JSON = os.path.join(HERE, "matritellus_release.json")


def parse_latest_from_readme():
    if not os.path.exists(README_PATH):
        return None
    text = open(README_PATH, encoding="utf-8").read()
    # Match rows in the Versiones markdown table: | 0.0.21 | 22/11/2026 | Notas... |
    rows = re.findall(r"^\|\s*(\d+\.\d+\.\d+)\s*\|\s*(\d{2}/\d{2}/\d{4})\s*\|\s*(.+?)\s*\|$", text, re.MULTILINE)
    if not rows:
        return None
    ver, date_str, notes = rows[-1]
    # Strip trailing release URL from notes if present
    notes_clean = re.sub(r"\s*https://github\.com/LomoXSoft/Matritellus/releases/tag/\S+\s*$", "", notes).strip()
    dd, mm, yyyy = date_str.split("/")
    iso_date = f"{yyyy}-{mm}-{dd}T12:00:00Z"
    tag = f"v{ver}"
    base_dl = f"https://github.com/LomoXSoft/Matritellus/releases/download/{tag}/Matritellus-{ver}"
    return {
        "tag_name": tag,
        "version": ver,
        "date": date_str,
        "published_at": iso_date,
        "notes": notes_clean,
        "assets": {
            "windows": f"{base_dl}-Windows.exe",
            "android": f"{base_dl}-Android.apk",
            "linux": f"{base_dl}-Linux.tar.gz",
        },
    }


def main():
    data = parse_latest_from_readme()
    if not data:
        sys.exit("Could not parse latest version from " + README_PATH)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Updated {OUT_JSON} -> {data['tag_name']} ({data['date']})")

    if "--push" in sys.argv:
        subprocess.run(["git", "-C", SITE_ROOT, "add", "LomoXGames/matritellus_release.json"], check=True)
        r = subprocess.run(["git", "-C", SITE_ROOT, "commit", "-m", f"Actualizar Matritellus a {data['tag_name']}"], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        subprocess.run(["git", "-C", SITE_ROOT, "push", "origin", "main"], check=True)


if __name__ == "__main__":
    main()
