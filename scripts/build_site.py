#!/usr/bin/env python3
"""Build the deployable Wahltrends information site."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
GENERATED_REPOSITORY_PATHS = (
    Path("impressum.html"),
    Path("en/legal-notice.html"),
)
ROBOTS_META = '<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">'
GOOGLEBOT_META = '<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet">'
UNRESOLVED_MARKER = re.compile(r"\{\{[A-Z_]+\}\}")
LEGAL_CONTACT_URL = "https://wahltrends.duckdns.org/legal/contact.html"
LEGACY_LEGAL_MARKERS = (
    "LEGAL_NAME",
    "LEGAL_ADDRESS",
    "CONTACT_EMAIL",
    "RESPONSIBLE_SECTION",
    "WAHLTRENDS_LEGAL_NAME",
    "WAHLTRENDS_LEGAL_ADDRESS",
    "WAHLTRENDS_CONTACT_EMAIL",
    "WAHLTRENDS_RESPONSIBLE_PERSON",
)
LEGAL_ROBOTS_DISALLOWS = (
    "Disallow: /impressum.html",
    "Disallow: /en/legal-notice.html",
)
LEGAL_ROBOTS_SEARCH_ALLOW_BLOCKS = (
    "User-agent: Googlebot\nAllow: /impressum.html\nAllow: /en/legal-notice.html",
    "User-agent: bingbot\nAllow: /impressum.html\nAllow: /en/legal-notice.html",
    "User-agent: OAI-SearchBot\nAllow: /impressum.html\nAllow: /en/legal-notice.html",
)


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("A build output directory is required.")

    if any((ROOT / path).exists() for path in GENERATED_REPOSITORY_PATHS):
        fail("Generated legal notice files must not be stored in the repository.")

    output = Path(sys.argv[1]).resolve()
    if output == ROOT or ROOT in output.parents:
        fail("The build output directory must be outside the repository.")
    if output.exists() and any(output.iterdir()):
        fail("The build output directory must be empty.")
    output.mkdir(parents=True, exist_ok=True)

    for filename in (
        "index.html",
        "privacy.html",
        "terms.html",
        "bildnachweise.html",
        "style.css",
        "robots.txt",
    ):
        shutil.copy2(ROOT / filename, output / filename)

    shutil.copytree(ROOT / "assets", output / "assets")

    (output / "en").mkdir()
    for filename in ("index.html", "privacy.html", "terms.html", "image-credits.html"):
        shutil.copy2(ROOT / "en" / filename, output / "en" / filename)

    shutil.copy2(ROOT / "templates" / "impressum.template.html", output / "impressum.html")
    shutil.copy2(
        ROOT / "templates" / "legal-notice.template.html",
        output / "en" / "legal-notice.html",
    )

    html_files = list(output.rglob("*.html"))
    if len(html_files) != 10:
        fail("The site build is incomplete.")

    for page in html_files:
        content = page.read_text(encoding="utf-8")
        if ROBOTS_META not in content or GOOGLEBOT_META not in content:
            fail("The site build is missing required robots metadata.")
        if UNRESOLVED_MARKER.search(content):
            fail("The site build contains unresolved template markers.")

    legal_pages = (output / "impressum.html", output / "en" / "legal-notice.html")
    for page in legal_pages:
        content = page.read_text(encoding="utf-8")
        if "data-nosnippet" not in content:
            fail("The legal notice is missing required snippet protection.")
        if LEGAL_CONTACT_URL not in content or "legal-contact-frame" not in content:
            fail("The legal notice is missing the protected external contact block.")
        if any(marker in content for marker in LEGACY_LEGAL_MARKERS):
            fail("The legal notice contains legacy embedded legal-contact data markers.")

    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    if any(marker in workflow for marker in LEGACY_LEGAL_MARKERS):
        fail("The Pages workflow must not inject legal-contact secrets.")

    robots_path = output / "robots.txt"
    if not robots_path.is_file():
        fail("The site build is missing robots.txt.")
    robots = robots_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if "User-agent: *" not in robots or any(rule not in robots for rule in LEGAL_ROBOTS_DISALLOWS):
        fail("robots.txt is missing legal-notice crawler restrictions.")
    if any(block not in robots for block in LEGAL_ROBOTS_SEARCH_ALLOW_BLOCKS):
        fail("robots.txt is missing search-crawler exceptions required for noindex processing.")

    print("Static site build completed.")


if __name__ == "__main__":
    main()
