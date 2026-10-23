# Paper Trail blog updates

The owner has given standing approval to translate every new or edited blog into
all nine existing languages: Spanish, Persian, Armenian, Simplified Chinese,
Korean, Tagalog, Telugu, Russian, and Arabic. Include the full articles, archive
cards, metadata, image alt text, language routes, and translation sitemap.
Paid Google Translation calls for that work are authorized. Do not ask again.

After editing English blogs, run `tools/update-blog-translations.ps1` (or
`tools/sync-blog-translations.py --refresh` using the available Python runtime
with Google authentication packages). It reuses the
existing project, saved translation fields, static routes, and page design.
Inventory without `--refresh` makes no paid calls. Reuse saved results; never
retry an uncertain paid call automatically. Do not treat untranslated English
copies as completed language versions. Verify all nine language archives and
article links before calling a blog update complete.

Keep work local. No commits, pushes, publishing, deployments, or live website
changes unless the owner separately authorizes them.

## Repository security and file protection

These instructions apply throughout this repository, including development tools,
verification folders and audit folders. Preserve all other project instructions.

- Never commit browser profiles or user-data directories, browser cookies, saved
  login databases, authentication snapshots, or sensitive browser session files.
- Create disposable browser profiles and testing output in system temporary
  directories outside Git repositories. Do not reuse personal or saved sessions.
  Preserve existing persistent browser workflows; flag their dependencies and
  obtain approval before migrating or changing them.
- Do not commit unnecessary generated screenshots, temporary testing logs, caches,
  temporary downloads, or other disposable testing artifacts. Retain approved
  reports, source snapshots and documentation; review uncertain files with the owner.
- Preserve legitimate website/application files, required development tools,
  images, icons, business data, translations, SEO/AEO content, configuration,
  sitemaps, forms, integrations and approved project reports.
- Respect existing .gitignore rules and pre-commit security hooks. Do not bypass
  or weaken them to stage suspicious files. Enable the repository's .githooks in
  each checkout where available; local hook activation does not follow a clone.
- Before every commit, inspect the complete staged file list, statuses and diff.
  Verify that only the explicitly approved changes are included and that required
  assets remain tracked. Run the staged-file protection check where available.
- Flag suspicious or sensitive files before committing. Report paths and exposure
  types only; never print or expose actual password, credential, token, cookie,
  private-key or session values in reports, logs or chat.
- Never rewrite Git history, force push, or change repository visibility without
  the owner's explicit approval.
- Never commit, push, deploy or publish without the owner's explicit approval.
  Approval for one action does not authorize a subsequent push or deployment.
- Never modify unrelated website content or application functionality.
- Do not delete local files or remove approved documentation/assets as incidental
  cleanup. Keep requested changes local and reviewable until approved.
