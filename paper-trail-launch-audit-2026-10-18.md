# Paper Trail Launch Audit — October 18, 2026

**Status: THE SITE IS NOT LIVE YET. The live audit could not be completed because the site does not serve yet.**

Checked repeatedly from 5:53 PM to 6:52 PM Pacific on October 18, 2026:

- `https://www.papertrailusa.com/` — the connection returns an empty reply every time (the page never loads at all).
- `https://dmduncananalyst.github.io/paper-trail/` — GitHub Pages returns its "Site not found" 404 page every time. This means Pages is not serving the repo yet, or the build has not gone through.
- `https://papertrailusa.com/` (no www) — loads a registrar parking page that redirects to `/lander`. The bare domain is pointing at a parking page, not at GitHub Pages.

Because the site is not serving, the on-screen checks (layout, photos, chat opening, clicking through pages in a browser) still have to be done once it is live. Everything below marked "checked in the site files" was verified against the exact files that were pushed to GitHub, which are the files Pages will serve. Nothing on the site was changed or fixed; this file is findings only.

---

## Critical

### 1. The site is not serving yet (launch blocker)
GitHub Pages answers "Site not found" for the repo, the www address never connects, and the bare domain shows a registrar parking page. Until Pages is confirmed on in the repo settings (Settings, Pages, source set to the main branch) and the www DNS record is confirmed to point at GitHub, no visitor can reach the site, and Search Console verification, sitemap submission, and indexing cannot start.

### 2. Typed chat questions will fail on the live site (checked in the site files)
The chat box has two parts. The guided question-and-answer flow is built into the site and has its answers translated. But when a visitor types their own free-text question, the site sends it to an address on the same domain, `/api/chat`, and waits for a reply. GitHub Pages is static hosting and has no such address, so every typed question will come back with an error instead of an answer once the site is live. The guided choices work; the type-your-own-question part needs a real backend behind it or it will look broken to visitors.

### 3. Internal working files are inside the site and will be public (checked in the site files)
The push included the whole working folder, not just the website. Once Pages serves the repo, anyone who guesses or finds these addresses can read them:

- The `tools` folder (the build and correction scripts).
- The `verification` folder (388 internal review pages, including screenshot folders and check files).
- Working documents at the top level, including `Paper-Trail-Master-Website-Instructions.md`, `SEO-AEO-Master-Audit.md`, `Paper-Trail-Saved-Google-Translations.txt`, the audit codex documents, the page inventory and priority fix list CSVs, and `START_HERE.txt`.

These are the business's internal instructions, audit notes, and fix lists. They should come out of the public site before they are found by a competitor or a search engine.

---

## High

### 4. All 500 state pages are missing from both sitemaps (checked in the site files)
The 50 state record pages exist in every language (50 states × 10 languages = 500 pages), and other pages link to them, but neither `sitemap.xml` nor `sitemap-translations.xml` lists a single one of them. Google can still find them by following links, but leaving them out of the sitemaps slows that down and means a sitemap submission does not cover them. The two sitemaps together list 1,420 pages; the site actually has about 1,920.

### 5. Five pages in every language are missing the chat section the other pages have (checked in the site files, needs one live confirmation)
137 of the 142 pages carry the conversation and chat markup. These 5 do not, in all 10 languages (50 page versions): `tax-ready-bookkeeping-records.html`, `profit-vs-cash-flow-business-money.html`, `nationwide-bookkeeping.html`, `los-angeles-county.html`, `catch-up-bookkeeping-overdue-books.html`. If the chat is supposed to appear on every page, these are the gaps. One live look once the site is up will confirm whether the chat truly is absent there.

---

## What checked out clean (verified in the site files)

### The fill-out form
There is no separate form page; the intake is the guided conversation on the pages. It collects name, company name, what needs attention, email, and phone, and it validates before sending: name, company, and the issue are required, the email must be a real email shape, and the phone must be ten digits. On the public site it is set to send straight to the HubSpot form (the direct-send switch is on in `assets/site.js`, endpoint in `assets/hubspot.js`), so the form does not depend on the missing `/api/` address the way typed chat does. No test inquiry was submitted. One live pass is still needed to watch a full submission go through.

### Languages
All 9 language folders (ar, es, fa, hy, ko, ru, te, tl, zh-CN) hold the full page set, 142 pages plus the 50 state pages each. Sampled pages in every language are genuinely in that language: Spanish and Tagalog samples are full of the right everyday words with almost no English mixed in, and the Arabic, Persian, Armenian, Korean, Russian, Telugu, and Chinese samples run 73 to 98 percent in their own script. No sampled translated page was a copy of the English page, and no sampled page was left in English. The chat input placeholder is translated on each language's pages, and the guided chat answer file holds all 825 entries in all 10 languages.

### Chat box language
The chat frame, its input placeholder, and the guided answers are translated per language in the files (see Critical item 2 for the one part that will not work, typed questions). Opening the chat in a browser in each language and reading the greeting on screen is still owed once the site is live.

### Links
112,182 internal links and image references were checked against the files that exist. Zero point at a missing page. Translated pages use a base address plus language-prefixed links, and they resolve correctly. 158 different outside links were found, almost all of them official state sources on the state pages, which matches the research those pages came from.

### Banned phrases
Every page and every script was searched for the banned generic phrases, including "next steps," "take the next step," "book a consultation," and "talk with me." Zero matches anywhere on the site.

### Page completeness
All 142 English pages have a title and a mobile viewport setting, and every one carries its language links. The shortest page still holds about 1,300 characters of real text. No empty or half-built pages were found by content. No package pricing appears anywhere on the site pages (the only matches for the package numbers were drawing coordinates inside an SVG graphic on the areas page).

### Robots file
`robots.txt` allows the whole site, blocks `/api/` and `/inquiries`, and points search engines at both sitemaps.

---

## Lower priority notes (checked in the site files)

1. Translated pages declare their language as, for example, `es-x-mtfrom-en` instead of plain `es`. That tag is the machine-translation marker. The language links between pages use the clean codes, so this is a correctness cleanup, not a breakage.
2. One script file, `assets/locales/ui.js`, is not loaded by any page, and it contains an old notice claiming the guided chat stays in English and messages are not sent. It does nothing today, but it contradicts how the site actually works and would confuse anyone who reads or loads it later.
3. A handful of the outside source links on the state pages still use `http://` instead of `https://`.

## Still owed once the site is live (needs the live site in a browser)

- Open every key page at desktop and phone widths and look for cropped photos, text running over anything, boxes covering words, and anything that does not fit the page.
- Open the chat box in each of the 10 languages and read the greeting on screen.
- Walk the intake conversation end to end and watch the fields, the validation messages, and the send button.
- Click the main menu and in-page links in a browser and confirm each one lands where it should. (File-level link checking is already clean, above.)

## Search Console, sitemap, and indexing

Not started, because it cannot start yet:

- The property for `https://www.papertrailusa.com/` cannot be verified while the site does not serve.
- The site has no Google Analytics tag, so the Analytics verification shortcut is not available. The verification routes that remain are: the HTML file method (a Google verification file has to be added to the top level of the repo, which is a repo change), the meta tag method (the tag has to be added to the homepage file in the repo, also a repo change), or a DNS TXT record at the registrar (done on the user's side).
- The moment the site serves and the property verifies, submit both sitemaps: `https://www.papertrailusa.com/sitemap.xml` and `https://www.papertrailusa.com/sitemap-translations.xml`.
- Indexing requests then go in this order, until the day's limit stops it: homepage (`index.html`), `services.html`, `paper-trail-services.html`, `faq.html`, `monthly-bookkeeping-review.html`, `tax-ready-bookkeeping.html`, `paper-trail-monthly-bookkeeping.html`, `nationwide-bookkeeping.html`, `los-angeles-county.html`, `areas-we-serve.html`, then the strongest service pages.
