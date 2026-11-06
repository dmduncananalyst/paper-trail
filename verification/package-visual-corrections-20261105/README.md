# Paper Trail screenshot, Payroll, and bundle corrections — November 5, 2026

This release completes the three approved correction requests together.

## Completed corrections in all ten languages

- Services and Packages dropdowns are centered immediately below their own
  labels, with viewport-edge protection. Hover, touch, keyboard entry, Escape,
  and outside-pointer closing retain the existing destinations and appearance.
  Navigation text increases from 15px to 16px on desktop and from 14px to 15px
  on phones. Desktop keeps eight items in one centered horizontal row.
- All Services uses six bordered cards with consistent padding and bottom
  buttons. Each existing View Service link also covers its entire card through
  a native stretched link. Names, descriptions, labels, destinations, and the
  introductory photograph remain byte-for-byte unchanged in the HTML.
- All six dedicated package pages share the approved Financial Analysis card
  borders, typography, spacing, and centered groups. Existing Enterprise names
  and Custom Quote wording are presented separately to match the reference.
  Repair keeps its approved Custom Quote presentation and existing four repair
  explanation cards. No repair prices, limits, or package tiers were invented.
- English approved recurring monthly amounts use the existing `/month`
  presentation. Other languages retain their exact saved frequency wording,
  rendered inline. Payroll processing schedule labels and approved monthly fee
  frequency are preserved. Setup fees, overages, limits, notices, checklists,
  terms, consultation controls, and quote destinations remain intact.
- Weekly Bookkeeping displays Bronze $700/month, Silver $1,300/month, Gold
  $2,100/month, and Enterprise Custom Quote on both its overview and dedicated
  page. The existing translated tier names and monthly currency/frequency
  templates are reused from the same language. No Financial Analysis service
  descriptions, limits, or price amounts were copied into Weekly Bookkeeping.
- The specified long Payroll service paragraph is split into exactly two
  paragraphs immediately before its existing Payroll Reporting text. Only
  paragraph tags are inserted. Every character of the original text and every
  existing heading remains unchanged. Tagalog retains the block's existing
  “Pag-uulat ng Payroll” wording, rather than substituting its separate heading's
  different saved wording.
- The final Bundle & Save overview card now has the headings “Bundle 1 —
  Bookkeeping + Financial Analysis + Payroll” and “Bundle 2 — Bookkeeping +
  Financial Analysis + Payroll + Accounts & Billing.” Each localized heading
  copies its own dedicated Bundle & Save page's exact wording. All six existing
  tier previews and all monthly/weekly prices remain directly underneath. The
  existing View Bundles link is unchanged. All ten separate Bundle & Save source
  pages remain unchanged.

## References and preservation

The exact files Screenshot (555).png through Screenshot (560).png were opened
from the owner's Screenshots folder. Their hashes are recorded in
`approved-source.json`; the screenshot images are not copied into Git. The
written request swaps the pricing screenshot filenames: the actual (557) shows
Financial Analysis and (558) shows Accounts & Billing. The actual Financial
Analysis design was used, as requested by name.

`approved-source.json` retains the 90 scoped pre-correction pages and the earlier
preservation hashes. The scoped verifier checks the exact permitted HTML
transformations, original link destinations, unchanged inclusion lists and
terms, and every numerical token. Only the three explicitly approved Weekly
amounts may be added. Bundle price-preview markup is compared separately and
remains identical. Sixty other service/Bundle & Save source files are unchanged;
the ten Payroll sources contain only the authorized paragraph-tag insertion.

No existing mandatory security, source-policy, translation test, build, launch
audit, Git hook, or deployment workflow was changed. The earlier reorganization
snapshot is retained as historical evidence; use the new scoped correction tool
for this later approved state rather than regenerating the older layout.

## Validation

- Source/translation preservation: 90 pages, 60 unchanged service/bundle sources,
  10 exact Payroll paragraph separations, and 20 copied bundle inclusion headings.
- Independent numeric, bundle-price, canonical, hreflang, sitemap, and saved
  language-selector checks passed for all 90 scoped pages.
- Browser matrix: 360 page/viewport checks across all ten languages at 1440,
  1024, 834, and 390 pixels; 120 actual whole-card/button navigations; 80 direct
  dropdown alignment, hover/touch, and closing checks. No horizontal overflow,
  broken images, JavaScript exceptions, or submitted forms were detected.
- Language selectors: 72 actual switches between English and each of the nine
  other languages across All Services, All Packages, Monthly packages, and the
  Payroll service page.
- Existing security self-test: all 26 blocked and 27 allowed cases passed,
  including NUL-delimited filenames, Unicode, and live ignore inspection.
- Existing source policy: 12 checks passed. Existing public source integrity:
  2370 pages, zero errors. Existing offline translation tests: 33 passed.
- Unchanged public build and launch audit passed: 2370 pages, 2370 sitemap URLs,
  174774 internal references, and zero errors. Whitespace checks passed.

Profiles, screenshots, and disposable browser results remain in system TEMP.
Unrelated local work is excluded from this release. The existing staged-file
guard and commit hook are required before committing; deployment and live
verification results are reported separately in the release handoff.

## Translation usage

New Google Translation requests: **0**. Characters dispatched: **0**. Incremental
translation cost for these corrections: **$0**. Existing translated wording was
copied, retained, or used as a template for the explicitly approved numeric
substitutions. No credentials, quotas, billing settings, cache protections, or
usage-ledger safeguards were changed.

Reproduce the scoped corrections with `tools/package_visual_corrections.py`.
Use `--verify` for preservation/SEO checks. Browser checks are in
`tools/test-package-visual-corrections.ps1`; `-InteractionsOnly` runs the language
switching checks without repeating the completed viewport matrix.
