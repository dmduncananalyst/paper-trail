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
