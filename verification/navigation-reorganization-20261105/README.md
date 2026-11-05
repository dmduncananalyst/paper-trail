# Navigation and package organization — November 5, 2026

The shared header now displays Home, About, Services, Packages, Bundle & Save,
Notes, Blog, and Contact Us in that order. Services and Packages contain one
flat menu each, using the existing language-specific labels. Desktop hover,
touch taps, keyboard entry, Escape, and outside-pointer closing are supported.
The existing header design, logo, colors, and typography are retained.

## Routes

The production origin is `https://www.papertrailusa.com/`.

- All Services: `all-services.html`
- All Packages: `packages.html`
- Weekly Bookkeeping packages: `weekly-bookkeeping-packages.html`
- Monthly Bookkeeping packages: `monthly-bookkeeping-packages.html`
- Bookkeeping Repair packages: `bookkeeping-repair-packages.html`
- Accounts & Billing packages: `accounts-billing-packages.html`
- Financial Analysis packages: `financial-analysis-packages.html`
- Payroll packages: `payroll-packages.html`

Each route has corresponding `es/`, `fa/`, `hy/`, `zh-CN/`, `ko/`, `tl/`,
`te/`, `ru/`, and `ar/` versions, canonical URLs, eleven hreflang entries,
saved language-selector routes, and sitemap entries. The route inventory is
extended through the existing public build and unchanged release workflow.

## Preservation and translations

`approved-source.json` retains the original package source HTML and the exact
category sections from each language, plus preservation hashes for the six
service pages and Bundle & Save page in each language. The 60 extracted package
sections contain no line breaks and match their original UTF-8 bytes exactly.
The original inline package styles, global package CSS, notices, disclaimers,
consultation controls, quote links, and shared billing boundaries are retained.

All 60 service source files and all 10 Bundle & Save source files remain
unchanged. Their shared header uses the new navigation controller. Service
overview descriptions and photograph alt text come directly from the existing
page in the same language. Overview prices and tier names come from that
language's original package sections. Weekly bookkeeping retains its approved
custom quote presentation. No prices or package tiers were invented.

The existing checkmark CSS color is `#405940` in
`assets/billing-refinements.css`; it is preserved along with the original
markup, rather than changing the approved package styling.

Only **View Packages** and **View Bundles** required new translation results:
nine completed Google calls, 225 source characters in total, with 18 saved
results. Existing package sections were never submitted for translation.
Durable successful receipts were reused after a local reporting error; no
uncertain paid call was retried. Actual provider charges are not reported by
the API and are not asserted here. The dedicated saved-label dictionary is
also loaded by the established translation cache for reuse in fresh checkouts.

## Local validation

- 60 exact section comparisons; 70 unchanged service/bundle source files.
- 80 canonical, hreflang, and language-selector route checks.
- 320 browser page/viewport checks across ten languages at 1440, 1024, 834,
  and 390 pixels. Eight desktop navigation items occupy one row. Hover and
  touch menus work without indicators or nested menus. No horizontal overflow,
  broken images, JavaScript exceptions, or form submissions were detected.
- Additional browser checks followed all 60 service cards, all 60 package
  cards, all ten bundle cards, both new language-switch destinations in each
  language, and the main Packages label in each language: 160 navigations.
  Keyboard menu entry and Escape passed in all ten languages.
- Security-hook self-test: 26 blocked and 27 allowed synthetic cases passed,
  including Unicode, NUL-delimited filenames, and live ignore inspection.
- Source-section policy: 12 checks passed. Public source integrity: 2370 pages
  checked without errors. Translation cache, accounting, uncertainty, reuse,
  lossless spans, and blog repair: 33 offline tests passed.
- The public build and unchanged launch audit passed: 2370 pages, 2370 page
  sitemap URLs, 174774 internal references, and zero errors.
- Whitespace checks passed. No security hooks, security configuration, or
  deployment workflow were changed.

Browser profiles and disposable screenshots/results are in system TEMP, outside
Git. No customer forms were submitted. Unrelated local files are excluded from
the release change set. A final build from the staged file inventory is required
before commit and publication; deployment and production results are reported
separately in the release handoff.

Regenerate locally with `tools/reorganize-service-packages.py`, which reuses the
saved sections and translations. `--verify` performs read-only content/route
checks and refreshes the approved integrity report. `--translate-new-text` is
only necessary if one of the two specifically authorized action labels is
missing; it never dispatches existing package sections or unrelated content.
