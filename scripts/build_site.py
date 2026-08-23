#!/usr/bin/env python3
"""Build the deployable Wahltrends site without exposing legal-notice secrets."""

from __future__ import annotations

import html
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ENV = (
    "WAHLTRENDS_LEGAL_NAME",
    "WAHLTRENDS_LEGAL_ADDRESS",
    "WAHLTRENDS_CONTACT_EMAIL",
    "WAHLTRENDS_RESPONSIBLE_PERSON",
)
GENERATED_REPOSITORY_PATHS = (
    Path("impressum.html"),
    Path("en/legal-notice.html"),
)
ROBOTS_META = '<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">'
GOOGLEBOT_META = '<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet">'
UNRESOLVED_MARKER = re.compile(r"\{\{[A-Z_]+\}\}")


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def escaped_lines(value: str) -> str:
    lines = [html.escape(line.strip()) for line in value.splitlines() if line.strip()]
    return "<br>\n".join(lines)


def render(template_path: Path, destination: Path, replacements: dict[str, str]) -> None:
    content = template_path.read_text(encoding="utf-8")
    for marker, value in replacements.items():
        content = content.replace("{{" + marker + "}}", value)
    if UNRESOLVED_MARKER.search(content):
        fail("Legal notice template configuration is incomplete.")
    destination.write_text(content, encoding="utf-8", newline="\n")


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

    values = {name: os.environ.get(name, "").strip() for name in REQUIRED_ENV}
    if any(not value for value in values.values()):
        fail("Required legal notice configuration is missing.")

    email = values["WAHLTRENDS_CONTACT_EMAIL"]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        fail("Legal notice configuration is invalid.")

    for filename in ("index.html", "privacy.html", "terms.html", "style.css"):
        shutil.copy2(ROOT / filename, output / filename)
    shutil.copytree(ROOT / "assets", output / "assets")
    (output / "en").mkdir()
    for filename in ("index.html", "privacy.html", "terms.html"):
        shutil.copy2(ROOT / "en" / filename, output / "en" / filename)

    legal_name = html.escape(values["WAHLTRENDS_LEGAL_NAME"])
    legal_address = escaped_lines(values["WAHLTRENDS_LEGAL_ADDRESS"])
    contact_email = html.escape(email)
    responsible_name = html.escape(values["WAHLTRENDS_RESPONSIBLE_PERSON"])

    responsible_de = (
        '<h3>Verantwortlich nach § 18 Abs. 2 Medienstaatsvertrag</h3>\n'
        f'<p><strong>{responsible_name}</strong><br>{legal_address}</p>'
    )
    responsible_en = (
        '<h3>Person responsible under section 18(2) of the German State Media Treaty</h3>\n'
        f'<p><strong>{responsible_name}</strong><br>{legal_address}</p>'
    )

    common = {
        "LEGAL_NAME": legal_name,
        "LEGAL_ADDRESS": legal_address,
        "CONTACT_EMAIL": contact_email,
        "CONTACT_EMAIL_ATTRIBUTE": html.escape(email, quote=True),
    }
    render(
        ROOT / "templates" / "impressum.template.html",
        output / "impressum.html",
        {**common, "RESPONSIBLE_SECTION": responsible_de},
    )
    render(
        ROOT / "templates" / "legal-notice.template.html",
        output / "en" / "legal-notice.html",
        {**common, "RESPONSIBLE_SECTION": responsible_en},
    )

    html_files = list(output.rglob("*.html"))
    if len(html_files) != 8:
        fail("The site build is incomplete.")
    for page in html_files:
        content = page.read_text(encoding="utf-8")
        if ROBOTS_META not in content or GOOGLEBOT_META not in content:
            fail("The site build is missing required robots metadata.")
        if UNRESOLVED_MARKER.search(content):
            fail("The site build contains unresolved template markers.")
    for page in (output / "impressum.html", output / "en" / "legal-notice.html"):
        if "data-nosnippet" not in page.read_text(encoding="utf-8"):
            fail("The legal notice is missing required snippet protection.")

    print("Static site build completed.")


if __name__ == "__main__":
    main()
