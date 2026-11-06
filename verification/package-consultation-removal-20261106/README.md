# Dedicated-package consultation removal — November 6, 2026

Reference: the exact `Screenshot (561).png` was opened and inspected. Its hash
is recorded with the approved source snapshot; the screenshot is not copied
into Git.

The redundant pricing-section Book a Consultation reveal controls were removed
from Weekly Bookkeeping, Monthly Bookkeeping, Accounts & Billing, and Payroll
in English and all nine existing additional languages: 40 removals on 40 pages.
Bookkeeping Repair and Financial Analysis already had no matching redundant
pricing-section control; those 20 pages remain unchanged and were verified.

Only the targeted `<details class="package-consultation">` controls outside
the pricing cards were removed. Their hidden calendar choices were removed
with the corresponding reveal control. No orphan controls were left behind.
The existing quote buttons beside them remain intact. Consultation controls
inside cards and the shared lower contact section are outside the removal scope.

## Preservation

- All 60 dedicated package pages were checked in all ten languages.
- All 240 pricing/repair cards are byte-for-byte unchanged, including Enterprise
  descriptions, prices, Request a Quote and Request a Custom Quote controls,
  destinations, and attributes.
- All package terms and billing boundaries are unchanged.
- All 60 retained shared contact consultation controls remain functional.
- All 2310 other approved source pages are unchanged, including service pages,
  overview pages, and the separate Bundle & Save pages.
- No CSS, application JavaScript, prices, descriptions, translations, metadata,
  language routes, sitemaps, security hooks, security settings, build scripts,
  existing mandatory checks, or release workflows were changed.
- Translation API requests: **0**. No forms were submitted.

The source snapshot and scoped verifier compare the complete resulting HTML
against the original with only the approved control spans removed. Pricing
cards, terms, and shared contact blocks are also compared independently. Other
pages are protected by their recorded source hashes. Unrelated local work is
excluded from this release.

## Local checks

- Existing security-hook self-test: all 26 blocked and 27 allowed cases passed,
  including NUL-delimited filenames, Unicode, and live ignore inspection.
- Existing source-section policy: 12 checks passed.
- Existing public source integrity: 2370 pages, zero errors.
- Existing offline translation/cache/accounting tests: 33 passed.
- Browser checks: 180 package-page/viewport checks at 1440, 834, and 390 pixels
  across all six categories and ten languages. No redundant controls remain;
  existing card quote buttons and retained consultation controls work. No
  horizontal overflow, broken images, JavaScript exceptions, or writes occurred.
- Unchanged public build and launch audit: 2370 pages, 2370 sitemap URLs,
  174774 internal references, and zero errors. Whitespace checks passed.

Browser profiles, screenshots, and disposable results stay in system TEMP.
The unchanged staged-file guard and commit hook must pass before committing.
Push, deployment, and live verification results are reported in the handoff.

Reproduce only this removal with
`tools/remove-package-standalone-consultations.py`; use `--verify` to check the
approved source boundary. Browser checks are in
`tools/test-package-consultation-removal.ps1`; `-Live` verifies the deployed
pages with a fresh temporary profile, blocks vendor requests, and submits no
forms.
