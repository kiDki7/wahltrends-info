# Wahltrends public information site

This repository contains only the public Wahltrends website and legal/API information. The Wahltrends bot and its private implementation are maintained separately and are not part of this repository.

The site is plain HTML and CSS. It has no framework, build step, npm dependency, analytics, cookies, tracking, advertising script, database or paid service.

## Publish with GitHub Pages

1. Open the `wahltrends-info` repository on GitHub.
2. Select **Settings** in the repository navigation.
3. In the left sidebar, open **Pages** under **Code and automation**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Set the branch to **main** and the folder to **/(root)**.
6. Click **Save**. Wait for the Pages deployment to finish; GitHub will show its status and public link on the same page.

The expected project URLs are:

- Homepage: <https://kidki7.github.io/wahltrends-info/>
- Privacy policy: <https://kidki7.github.io/wahltrends-info/privacy.html>
- Terms / API information: <https://kidki7.github.io/wahltrends-info/terms.html>

All internal links are relative filenames, so they work when the site is hosted below `/wahltrends-info/`.

## Before publishing

Replace every visibly marked placeholder in the HTML files:

- `[CHANNEL URL PLACEHOLDER]` and the temporary `https://www.youtube.com/` link in `index.html` with the exact public Wahltrends YouTube channel URL.
- `[OPERATOR EMAIL PLACEHOLDER]` in `privacy.html` with a public contact email for privacy questions and complaints.

Do not add API credentials, OAuth secrets or tokens, GitHub Actions secrets, private repository URLs, internal infrastructure details, SFTP credentials or a private home address to this repository.