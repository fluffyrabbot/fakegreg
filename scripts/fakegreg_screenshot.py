#!/usr/bin/env python3
"""Capture screenshots of HTML specimens via local Chrome headless."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fakegreg_lib import ROOT, choose_rendered_artifact, discover_specimens


DEFAULT_CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
    Path("/usr/bin/chromium-browser"),
]


def find_chrome(explicit: str | None = None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise FileNotFoundError(f"Chrome not found at {path}")
        return path
    env_chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if env_chrome:
        return Path(env_chrome)
    for candidate in DEFAULT_CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No Chrome/Chromium binary found. Pass --chrome /path/to/chrome "
        "or install Google Chrome."
    )


def screenshot_html(
    html_path: Path,
    out_path: Path,
    *,
    chrome: Path,
    width: int = 1440,
    height: int = 900,
    timeout_s: int = 60,
) -> None:
    html_path = html_path.resolve()
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Chrome --screenshot writes next to CWD by default when given a bare name;
    # use absolute path for the screenshot flag.
    with tempfile.TemporaryDirectory(prefix="fakegreg-shot-") as tmp:
        tmp_shot = Path(tmp) / "shot.png"
        url = html_path.as_uri()
        cmd = [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={width},{height}",
            f"--screenshot={tmp_shot}",
            url,
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        if proc.returncode != 0 and not tmp_shot.exists():
            raise RuntimeError(
                f"Chrome screenshot failed (code {proc.returncode}): "
                f"{(proc.stderr or proc.stdout or '').strip()[:400]}"
            )
        if not tmp_shot.exists() or tmp_shot.stat().st_size == 0:
            raise RuntimeError(f"Chrome did not write a screenshot for {html_path}")
        out_path.write_bytes(tmp_shot.read_bytes())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screenshot HTML specimens with local Chrome headless.")
    parser.add_argument(
        "--specimen",
        action="append",
        default=[],
        help="Specimen id to screenshot (repeatable). Default: all.",
    )
    parser.add_argument("--html", type=Path, default=None, help="Screenshot a single HTML file.")
    parser.add_argument("--out", type=Path, default=None, help="Output PNG path (with --html).")
    parser.add_argument("--chrome", default=None, help="Path to Chrome/Chromium binary.")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing screenshots even if present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    chrome = find_chrome(args.chrome)

    if args.html:
        out = args.out or args.html.with_suffix(".png")
        screenshot_html(args.html, out, chrome=chrome, width=args.width, height=args.height)
        print(f"Wrote {out} ({out.stat().st_size} bytes)")
        return 0

    specimens = discover_specimens()
    selected = args.specimen or sorted(specimens.keys())
    failures = []
    for specimen_id in selected:
        if specimen_id not in specimens:
            failures.append(f"{specimen_id}: missing")
            continue
        specimen_dir, manifest = specimens[specimen_id]
        html_path = choose_rendered_artifact(specimen_dir, manifest)
        if html_path.suffix.lower() not in {".html", ".htm"}:
            print(f"SKIP {specimen_id}: rendered artifact is not HTML ({html_path.name})")
            continue
        shot_rel = manifest["artifacts"]["screenshot_path"]
        out_path = specimen_dir / shot_rel
        if out_path.exists() and not args.force:
            print(f"KEEP {specimen_id}: {out_path.relative_to(ROOT)} already exists (use --force)")
            continue
        try:
            screenshot_html(html_path, out_path, chrome=chrome, width=args.width, height=args.height)
            print(f"WROTE {specimen_id}: {out_path.relative_to(ROOT)} ({out_path.stat().st_size} bytes)")
        except Exception as exc:  # noqa: BLE001 - surface all capture failures
            failures.append(f"{specimen_id}: {exc}")
            print(f"FAIL {specimen_id}: {exc}")

    if failures:
        print("\nScreenshot failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
