# Launch audit fixes — October 20, 2026

The October 18 audit was read in full. Existing layout, articles, saved translations, navigation and direct HubSpot intake were retained.

## Implemented

- Typed questions use existing published bookkeeping answers directly, without requesting the nonexistent GitHub Pages `/api/chat` endpoint. Published-answer selection supports all ten languages. This is a curated reference flow; no AI backend or credentials are required.
- Restored the translated conversation dialog and launch button on the five affected pages in every language (50 versions), with distinct page identifiers and page-specific intake topics.
- Added all 500 state pages to the existing sitemaps. Together the maps now contain all 1,920 public pages.
- Normalized the 1,728 translated HTML language declarations and the shared script that previously restored the machine-translation marker after loading.
- Corrected fragment links on pages with a document base so the skip-to-content link stays on the current page instead of navigating to the homepage.
- Removed the unused `assets/locales/ui.js` containing obsolete chat notices.
- Upgraded twelve official source addresses to HTTPS across all languages. Nebraska's obsolete host was replaced with the working official PDF address.
- Added an allowlisted public-site build, GitHub Pages Actions workflow, and a defensive Jekyll exclusion configuration. Internal tools, verification files, Markdown audits/instructions, CSV inventories and working text files are excluded from the website artifact. Required translation data, media, fonts and license files remain included.
- The deployment workflow runs the complete static verification before uploading the artifact.

## Verification

- Public build: 1,920 HTML pages, 1,420 conversation configurations, 1,920 unique sitemap URLs, and 115,508 local links/asset references; zero errors. State guides retain their original design without conversation dialogs.
- Headless Chrome: 14 key pages at 390px and 1440px (28 layout checks); no horizontal overflow or broken images.
- All ten language homepages: translated greetings, correct chat direction, complete intake, invalid email/phone validation, review/edit, mocked HubSpot confirmation, typed-question fallback and published-answer selection.
- All 50 restored dialogs opened successfully in the browser.
- Browser regression recorded zero JavaScript exceptions and zero requests to `/api/chat` or `/api/inquiry`.
- Browser menu expansion/Escape, main-menu page navigation, in-page skip navigation, and failed-delivery recovery passed. A simulated delivery failure retained the intake details and offered a retry.
- Screenshots and machine-readable results: `verification/launch-audit-20261020/`. Test scripts are in `tools/launch-*-qa.ps1` and `tools/verify-launch-audit.ps1`.
- Source checks: ten of the twelve upgraded source addresses returned HTTP 200 (including the corrected Nebraska PDF). Kansas and Maine returned HTTP 403 to automated checks, so their destination content could not be confirmed.
- No real customer inquiry was submitted; delivery payloads and confirmations were tested using mocked HubSpot responses.

## External launch blockers

Authenticated GitHub inspection confirmed the repository is public, the account has administrator access, and Pages is disabled (`has_pages: false`, Pages API 404). A later GitHub sign-in was cancelled, preventing the attempted Pages configuration update.

1. Enable repository Settings → Pages → Source: **GitHub Actions**, with custom domain `www.papertrailusa.com`. The included workflow deploys the allowlisted artifact after a push to `main`.
2. Correct the registrar's `www` CNAME: it currently points to **`dmduncanalyst.github.io`**, which is misspelled. The repository owner's correct target is **`dmduncananalyst.github.io`**.
3. Remove the bare-domain parking A records **`3.33.130.190`** and **`15.197.148.33`**. Retain the GitHub Pages A records **`185.199.108.153`**, **`185.199.109.153`**, **`185.199.110.153`**, **`185.199.111.153`**. Registrar access is unavailable here.
4. After DNS resolves and GitHub provisions the custom-domain certificate, enable Enforce HTTPS. Current custom-domain requests fail certificate validation; the repository Pages URL returns 404 while Pages is disabled.
5. Search Console requires account access and a property verification token/file or DNS verification. No token was supplied. Verify the property, submit both existing sitemap URLs, then request indexing in the audit's specified order.
6. Once hosting and DNS are fixed, repeat the browser smoke tests on the public domain and confirm one authorized real HubSpot delivery. Local browser tests cannot establish production TLS or actual inbox/CRM receipt.

The deployment exclusions protect the hosted website. Because the GitHub repository itself is public, source files and historical commits remain accessible on GitHub; removing that access requires repository visibility/history decisions outside this website build.
