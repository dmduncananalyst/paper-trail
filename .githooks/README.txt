LOCAL FILE PROTECTION

Enable for this checkout: git config --local core.hooksPath .githooks
Disable reversibly: git config --local --unset core.hooksPath
The local setting is not copied by cloning. Enable it in each new checkout.
No existing hooks were replaced. Hook scripts are project development tools.

The hook uses Git and Windows PowerShell (or PowerShell 7). On Windows it uses
ExecutionPolicy Bypass for this process only; it changes no execution-policy setting.
It reads staged filenames and paths, not file contents or credential values.
It blocks browser databases/profiles, credential environment files, authentication
snapshots, Python caches, new disposable test captures, and newly forced-added
ignored files. Staged deletions are allowed. Existing retained report images can
be edited; new assets in website assets/ and approved source/reference directories
are not treated as test captures. Reports, translations and application code are
not excluded by file extension. Private data rules still apply everywhere.

Run in a configured checkout: git hook run pre-commit -- -SelfTest
This tests synthetic paths and live read-only Git filename inspection; no browser,
fixture files, commits, network requests, or test index are created.

Keep disposable output under system TEMP or .local-test-output, never assets/.
For an intentionally approved new file excluded by a rule, review and narrowly
correct that rule rather than disabling protection. Existing ignored source
snapshots/reference files may still need owner review before being added.

Limits: filenames cannot identify every possible secret. Hooks can be bypassed
(e.g. --no-verify), modified, or disabled and do not enforce GitHub-side policy.
These are local preventive checks, not a security guarantee or a history cleanup.

REPOSITORY REVIEW
55 browser-related scripts reviewed. The existing PowerShell browser profiles already use TEMP/paper-trail-preview-<port>; Playwright uses temporary profiles. The shared port/profile reuse is preserved. Repository verification output includes retained reports, source snapshots and referenced images, so relocating this mixed output requires a separately reviewed input/output split.

System TEMP was verified outside all six checkouts. No browser was launched to test these changes. New clones require local activation; Unix hosts also require an executable hook and PowerShell 7. Nothing is staged or committed by this setup.
