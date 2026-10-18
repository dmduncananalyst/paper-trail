# PAPER TRAIL — MASTER WEBSITE DESIGN, CONTENT, NOTES, MULTILINGUAL AND PUBLISHING INSTRUCTIONS

**Status:** FINAL CONSOLIDATED CREATIVE + TECHNICAL BRIEF for Codex. Read the WHOLE document and inspect actual files and user-provided screenshots before changing code. This document supersedes earlier Paper Trail prompts. **Design must be visually completely new; preserve the approved underlying ideas, interactions, media, and brand colors.**

## 0. Non-negotiable working rules

1. Inspect the actual Paper Trail repository, existing site, content, assets, image dimensions, CSS, JavaScript, navigation, Notes content, chat integration, HubSpot connections, build/deploy workflow, and existing localization infrastructure **before** coding. Do not assume a system exists because this brief describes a desired feature. If the folder is empty or required assets/content are absent, report this clearly and do not invent missing brand materials or credentials.
2. Preserve Paper Trail's **existing brand colors**. Preserve functional interactions, useful homepage information architecture, existing approved copy, working links, images and integrations unless a specific change is authorized below. Don't turn “redesign” into an unrelated rebuild that loses what already works.
3. The user will supply screenshots of **StartWeb7, Paradigm Janitorial, and DommyDom Blog pages**. These are **negative design references**: study them to identify layouts, card grids, visual motifs and design habits that **Paper Trail must not resemble**. Do not copy or lightly recolor those sites. The separately supplied **Glow Rituals** reference is the **POSITIVE, SPECIFIC DESIGN REFERENCE** for BOTH the Notes listing photo cards AND the individual Notes reading pages. Match its visual treatment, white icons above titles on photos, hierarchy, photography/text integration, and overall aesthetic closely, while adapting subjects/icons/text to Paper Trail, preserving Paper Trail's own brand colors, photos, and existing card dimensions. This must not be interpreted as only an icon-placement reference. The three other websites are **negative references** for repetitive blog-page patterns, NOT instructions to abandon the Glow Rituals Notes treatment. If any referenced screenshot hasn't been supplied to Codex yet, wait to compare that screenshot before finalizing that design rather than claiming to have examined it.
4. Audit and actively use the **full available Paper Trail photo library**, including previously used and newly generated photos. Match unused photos to appropriate site sections, services, Notes topics, and other content rather than limiting the redesign to the few photos currently visible. Avoid unnecessary duplication. **Do not replace, regenerate, upscale artificially, stretch or enlarge photos** to support a new design. Check their actual resolutions before determining display sizes. Keep their current approved card/image sizes and proportions, or use consistently sized image frames that fit the assets without degrading them. Avoid a long oversized photographic hero that makes images blurry.
5. **All existing videos are non-negotiable: keep EVERY video in exactly its current section/location, preserve its source, playback, controls and surrounding functionality. Do not move, remove, reorder or swap videos during redesign.**
6. Maintain responsive, accessible design for desktop, tablet and mobile. Do not create dead buttons, fake interactions, duplicate menus, clipped headings, or poor color contrast. Test right-to-left translations.
7. Work locally only. **Do not commit, push, deploy, publish, enable paid services, create Google credentials, trigger actual translation billing, or change HubSpot production configurations without explicit approval.** Begin with audits, mockups and safe dry runs.
8. Do not introduce stock AI-template aesthetics: repeated oversized rounded tiles, generic finance icon packs, empty whitespace, identical SaaS grids, meaningless gradients, or robotic question-based copy. Pursue a cohesive, distinctive design actually specific to Paper Trail.

## 1. Overall design direction

The current site has valuable ideas, particularly the **homepage structure, usable interactive cards, content grouping, and the way visitors navigate subjects**. Keep those concepts and working behavior. **Completely rethink their visual execution**, including composition, card treatment where allowed, proportions of surrounding sections, illustration/icon language, typography hierarchy and rhythm. This must be a **total visual reinvention of every page**, not merely changed colors, font sizes, shadows, corner radii or spacing. **The user must NOT recognize the former build visually**: no recognizable old section compositions, card styling, navigation, icon set, decorative motifs, or overall template. The sole deliberate visual reference for the Notes cards and reading pages is Glow Rituals. Preserve the **concepts and working behaviors**, not the prior styling. Do not confuse “preserve homepage” with “preserve its appearance”: homepage structure of ideas, cards and interactions stay; its actual presentation becomes completely new. **Keep every video in its exact current location.** Keep the existing Paper Trail palette.

Paper Trail is a bookkeeping / financial-records business: communicate clarity, precision, humanity, reliability and calm professionalism, **without** looking like a generic accounting SaaS template. Avoid invented credentials, promised results, unsupported claims, fabricated testimonials, or unsupported service offerings. Preserve the site's real message and service taxonomy.

## 2. COMPLETELY redesign the menu

The current Paper Trail **menu is disliked**. Redesign its navigation structure, opening experience, arrangement, interaction and responsive behavior substantially. Do not just recolor the same menu or tweak the typography. Make destinations instantly understandable with clear labels and few clicks; don't hide important categories under redundant submenus or add confusing hover traps. The menu must work by mouse, keyboard and touch, including translated text, long words, and Arabic/Farsi right-to-left layouts. Avoid obstructive overlays and menu panels that cover essential controls or flash during page loads.

**Preserve every legitimate navigation destination and its working URL/functionality.** Design around the real site map. Make all menus, headings and controls shown on the translated Home and Notes pages display in the chosen language; do not imply the entire site is translated. Test the open and closed state in desktop/tablet/mobile views.

## 3. Visible page titles — EVERY page

Every page must present a clear, visible heading naming the actual page (**H1**, semantically correct), not only a browser-tab `<title>`:

- Notes index/listing: **Notes**.
- Each individual Notes/article page: **the exact article title** (its own visible H1).
- All other pages: a descriptive heading stating that page's name/purpose; keep the Homepage's appropriate real main heading rather than adding an awkward redundant “Home” label if the existing hero already functions as the H1.

Preserve the SEO document title, canonical, metadata and heading hierarchy independently. No missing or duplicated H1s.

## 4. Notes LISTING — match Glow Rituals, NOT the other sites

**The section is called “Notes,” not “Articles.”** Remove article-count labels such as “8 articles,” “12 articles,” counts on Notes categories and cards, and repeated count metadata anywhere in the Notes UI. Avoid the standalone UI label “Articles” on the Notes index/category cards. The action label **“Read Article” is acceptable** when it fits, as is a relevant “Read About [specific topic]”. Do not add counts back elsewhere.

**No “Explore” calls to action.** Specifically, never “Explore Tax Ready Bookkeeping,” “Explore...” or “Discover...” as substitutes for clear navigation. Use informative, natural, subject-specific actions, such as **“Read About Balancing and Corrections”** or **“Read About Bookkeeping”**, adjusted to the *actual* target page. Links must describe where they go and point to the correct destinations. Avoid question-style section and article headings simply to make navigation interactive. Preserve existing editorial titles that are already approved; don't indiscriminately rename real article titles.

The user will attach screenshots of the existing **StartWeb7**, **Paradigm Janitorial**, and **DommyDom** blog listing pages. Their layout conventions are overused across the user's projects. The Paper Trail Notes listing must follow the **Glow Rituals screenshot as its affirmative visual reference**, and look **materially different** from the other three sites in composition, hierarchy, navigation, grouping, image integration and editorial feel. Keep the approved card concept and dimensions, but change the visible style to closely capture Glow Rituals (image-backed card, beautiful topic-specific white icon above the title, legible title/link integrated over the photo), fitted to Paper Trail assets and brand. Do not default to the same blog-grid template used elsewhere. Develop a distinctive, editorial presentation within the constraints of existing image resolution. **Do not enlarge image regions into long/wide hero banners** if they will look blurry.

### Card/image consistency and the photographic icon treatment

- **Every card of the same kind is the same size**, with matching image-frame width, height and aspect ratio. All Notes photos occupy **consistently sized image frames** and remain sharp. Long titles must wrap gracefully without making sibling card/image dimensions inconsistent; choose a considered text allocation and avoid cutting meaningful text off. Responsive grids may change the number of columns, but peer cards remain visually consistent.
- Keep current approved dimensions where practicable; inspect photo pixels first. Use `object-fit` thoughtfully; do not arbitrarily crop important content, and never stretch photos. If source aspect ratios differ, provide consistent frames with non-distorting fitting instead of presenting random photo/card sizes.
- The user specifically wants the **Glow Rituals screenshot's** treatment: a **small, elegant white topic-related icon centered above each title, with icon and title over the photograph**. Apply this treatment consistently to Notes photo cards, preserving the approved dimensions and generated photos. Use distinct but consistent icons relevant to the exact topic (balancing/corrections, reconciliation, recordkeeping, payroll, cash flow, budgeting, tax preparation, etc.). These are **separate accessible SVG/design elements**, not baked into photographs, no emoji and no generic mismatched icon pack.
- Ensure icon, title and readable link are legible over each image, with a restrained localized overlay rather than flattening all photos under a heavy tint. Preserve content, real target links, keyboard focus and clickable area.
- No duplicate title, article count or excerpts. Don't add “Articles” badges or category counters.

## 5. Individual Notes pages — match Glow Rituals too

**The Glow Rituals screenshot governs not only the Notes listing cards, but ALSO the individual Notes/article page visual treatment.** Each article must have its OWN exact visible title/H1 and a meaningful corresponding elegant white subject-specific icon within a photo-led, carefully art-directed heading/intro that matches the Glow Rituals reference aesthetic. Adapt gracefully to available image resolution: no huge blurry hero images or stretching, no intrusive icons over text, no generic recycled blog-article layout from the negative examples. Preserve full article copy, source links, dates where already approved, SEO and links. **Do not turn articles into questions, or translate the full individual articles.**

## 6. Homepage — preserve what it does, replace how it looks

The user **LIKES the existing homepage**: its organization, card concepts, interactive behaviors, core content and the way visitors move through it. **DO NOT throw those away**. But the new homepage must **LOOK ENTIRELY DIFFERENT** from the previous build: new compositions, art direction, photo integration, bespoke icon system, revised card aesthetics, typography/hierarchy, visual flow and sectional treatments. No visible reuse of former homepage visual patterns. **Use the supplied photographs extensively and intelligently**, beyond the few currently displayed, while keeping them sharp. **Keep all homepage videos exactly where they currently are; no video may be moved, removed, replaced or reordered.** Keep current brand colors, working cards and features, exact link destinations, real copy and approved functions. No new question-form cards, generic accounting-template copy, meaningless CTAs or “Explore.”

## 7. Translation scope — ten language choices in total

**English is the default, plus exactly nine translated language choices** matching DommyDom:

| Code | Language shown in its native name |
|---|---|
| `en` | English |
| `es` | Español |
| `fa` | فارسی |
| `hy` | Հայերեն |
| `zh-CN` | 中文 |
| `ko` | 한국어 |
| `tl` | Tagalog |
| `te` | తెలుగు |
| `ru` | Русский |
| `ar` | العربية |

For the initial multilingual experience, **ONLY the Homepage and the main Notes listing page** are translated. Full individual Notes article pages and the remaining pages are **English**. Translate the visible static and client-rendered UI on the two supported pages: visible headings, summaries, card titles/previews, navigation labels shown there, CTAs, manual language menu, and chat widget UI. Carry the selected language when going between Home and Notes, but do **not** automatically switch based on browser language and do not pretend the entire site is multilingual. Default English should behave normally and should not show a translation notice.

**Short notice on BOTH translated pages**, small and unobtrusive, directly below the header and above the main page content, visually following the compact DommyDom pattern (no box, banner, modal, “Disclaimer” heading or explanation paragraph):

> **Only the Home and Notes pages are available in this language.**

Show the notice translated into the selected language. If full Notes articles remain English, the Notes listing must also make that clear in a **short localized note at the article links**, using the approved compact style, without suggesting full articles are translated. Do not cover navigation or introduce layout flashes when switching languages.

The header's language control should display the **currently selected language in its native name**, not a permanent teaser of other languages. Offer all ten choices. Retain selection between Home and Notes; other pages remain English, and navigation to them must not misrepresent their language availability. Respect RTL direction for Arabic and Farsi without breaking numeric values, brand names, or menus.

## 8. AI chat and HubSpot — multilingual, but genuinely functional

On translated **Home and Notes** pages, the **user-facing chat** must support the selected language: open/close labels, welcome message, questions/prompts, buttons, form labels, validation, and back-and-forth replies. Chat should handle free-typed messages and answer or guide people **in the chosen language** if there is a real functioning language-capable chatbot backend; do not pretend a static translated menu constitutes multilingual free-form AI. Translate messages or route responses securely as appropriate, without exposing API keys or private credentials in public JavaScript.

**Audit the current implementation before changing anything:** the user believes HubSpot forms and connections are already configured. Verify the real portal, form IDs, field mapping and existing submit flow **in the project**; do not copy IDs from another website or silently replace working HubSpot integrations. Preserve chat routing, existing conversational behavior and leads. Ensure the original message, selected language, contact information and page context are recorded appropriately when submitted. Avoid collecting financial account credentials or highly sensitive records through an insecure public chat. If multilingual free-form AI requires a new paid API, backend, translation call or hosting, propose it explicitly with cost/security implications and **do not enable it without approval**. Don't claim it works until a real end-to-end test succeeds.

The translated site's permanent static UI and cached blog previews must **not** trigger Google translation API calls on visitor page loads. If a live conversational model is used, document its separate possible per-message cost instead of confusing it with cached static translations.

## 9. Permanent translation files — initial Home and Notes content

Reuse the **existing Google Cloud Translation project** already used for DommyDom; no new project, Google account, API enablement or credentials unless genuinely required and explicitly approved. Design the one-time translation workflow to:

1. Extract **unique English strings** from the approved final Home and Notes listing pages, including JavaScript-rendered UI strings and notices, not only static HTML.
2. Translate to the nine target languages **once** with the standard eligible model and store them in **version-controlled static locale files** or another clearly documented permanent content store within the site's build. Retain safe HTML, placeholders, links and accessible labels.
3. At page load, read **saved local translations only**; no client-side calls to Google Cloud Translation. Fallback to English for missing strings and report gaps in testing.
4. Support changes using stable content IDs plus source-content hashes/versioning so unchanged strings are never billed twice. Preserve existing translations on rebuilds.
5. Validate all nine languages, RTL rendering, mobile layout and translated card link destinations. Never use Google machine translation to invent financial advice or alter service claims.

**Approval gate:** First build extraction, storage, rendering, verification and dry-run tools. Do not actually call Google or turn on billing until explicit approval. Provide estimated input-character counts, multiplied by each target translation, before any initial batch.

## 10. AUTOMATIC DAILY Notes translations — mandatory permanent-save workflow

The user plans roughly **three new Paper Trail Notes posts daily**, along with **six DommyDom** and **three StartWeb7** posts daily: **12 English posts/day across three sites**. For each new or edited Notes post, automatically during the controlled authoring/build/publishing workflow (not during web visits):

1. Detect the post's new or changed **English title, short card description/excerpt and other genuinely dynamic listing metadata**. Full article body stays English. Reuse static UI translations; don't retranslate common labels on every post.
2. Compute stable IDs and hashes for source fields and check the persistent cache. Translate **only untranslated/changed fields** into the nine target languages, and save translations permanently alongside the site data. Update the translated Notes cards and links before publishing.
3. Ensure idempotent runs: same input twice makes **zero** new API requests on the second run; changes to one excerpt do not cause the entire page to be translated again.
4. Track translated characters **per language, per site, per month** in a persistent, auditable shared ledger or safely coordinated central budget service, with estimated additional usage/cost shown **before** calling Google. Shared usage means independently installed scripts in three repositories must **not** each assume they have the entire allowance. Handle concurrent publishes without overspending because of race conditions.
5. During the free trial, usage may consume trial credits after the applicable free translation allowance. The ongoing target after trial is **at most $10/month additional standard translation cost across these three sites**. Verify Google's actual current price and free tier and estimate conservatively. Distinguish estimates from provider billing. **Google budget alerts are NOT hard spending caps. No local script can guarantee an account-wide cap against requests outside that script.** Don't promise otherwise.
6. When the shared budget guard would be exceeded, stop **before** requesting that translation batch; publish/update English content safely and mark missing target-language fields as **pending**, with a clear report. Never show made-up translations and never make uncontrolled retries. Avoid partial silent successes; reconcile and report by field/language.
7. Generate a concise build report: new posts, changed fields, cache hits, calls proposed/used, characters by language, total shared spend estimate, pending items, and whether the build was safe to publish.
8. Prefer a **manual, explicitly approved publish-time command or approved CI job**, rather than an always-running paid service. If truly automatic background scheduling is requested, first present the cost, hosting, credentials, safeguards and activation mechanism for approval. Do not rely on an editor being open or a temporary Cloud Shell session to maintain automatic updates.
9. Never expose Google credentials to client pages or a public GitHub repository. Prefer least-privilege secure credentials/secrets only in a controlled publishing environment. Do not place keys into MD files, web source code or logs.
10. Build and test the entire workflow first using **mock responses/DRY RUN and zero real Google calls**. Include tests for a new post, edited title, edited excerpt, duplicate run, exceeded shared budget, Google unavailable, one language failing, cached locale preservation and RTL UI. Only after approval connect live Google Translation and test with a small controlled batch.

## 11. Publishing, technical SEO and quality requirements

Preserve or implement correct Notes URLs, internal links, visible article H1s, meta titles/descriptions, semantic headings, canonical tags, sitemap entries and appropriately translated page text. Avoid inventing nine fake full-article translations or automatically creating duplicate URLs if actual localized content does not exist. Decide and document how language variants are represented and how search indexing will distinguish them; add `hreflang` only for genuine equivalents and correct canonical behavior. Keep the English version as source of truth. No SEO claims about rankings or guaranteed leads.

Prevent translation/layout “flash”: render correct saved locale as early as feasible, reserve UI dimensions, and avoid showing another language or menu overlay briefly on navigation. Test Home → Notes → English-only article → back, and switching language on each supported page. Verify no overlays obscure the menu.

## 12. Deliverables and approval checkpoints

**Phase A — inspect and propose without changing production:** report actual project state, missing screenshots/assets, image resolution constraints, current working HubSpot/chat situation, how the current site deploys, and a concrete custom design direction for the Notes page and new menu. Explain specifically how it differs from StartWeb7, Paradigm Janitorial and DommyDom *after* reviewing the supplied screenshots. Identify where current cards and photo dimensions are defined. Present a small representative **desktop + mobile visual prototype or screenshots** for user approval before extensive redesign.

**Phase B — local site implementation:** after visual direction is approved, implement menu, Notes presentation, page H1s, matched card/image sizing, subject-specific white photo-overlay icons, natural CTA wording, and responsive/accessibility fixes. Preserve working content, branding and HubSpot flows. Provide accurate screenshots and a concise changed-file list.

**Phase C — translation implementation, dry run:** create ten-choice manual selector, saved static translation architecture and UI, short notices, localized chat interface, and translation extraction/cache/build scripts. Demonstrate nine languages without live API calls initially (use clearly labeled mocks for missing locales). Verify current live AI/chat capabilities separately rather than simulating completion.

**Phase D — approval before live paid/API work:** show exact character estimates, credentials/secrets approach, translation quota/spend controls, independent real-time usage limitations, and a small test plan. Request explicit permission **before** live Google calls, connecting additional paid AI functionality, modifying HubSpot settings, committing, pushing or publishing.

### REQUIRED visual references and sequencing

The user will provide (A) **Glow Rituals** screenshot(s) as the POSITIVE reference for Notes cards AND individual Notes article pages; (B) screenshots of **StartWeb7, Paradigm Janitorial, and DommyDom blog pages** as NEGATIVE references for stale, repeated layouts; and (C) a folder/library of Paper Trail photography. **Do not claim to have reviewed screenshots that are not attached yet.** Match the Glow Rituals reference closely in treatment, NOT the physical pixel dimensions of photo cards. Do not start final visual implementation of the Notes pages until the reference arrives. Do not treat negative references as a command to use long horizontal hero images. Preserve the available image resolution. 

**Use English plus nine translations only: ten total language choices.** Show a small, unboxed sentence at the top of Home AND Notes only when translated: "Only the Home and Notes pages are available in this language." Place discreet Google-required translation attribution in the **bottom/footer**, not in a large top banner. Exact attribution/link must be compliant with current terms; do not invent a Google logo or omit obligatory notices. Full individual Notes are English. Match DommyDom's functional language-selector behavior (selected native language, manual selection retained across supported pages), not DommyDom's appearance.

### Final acceptance checklist

- [ ] Paper Trail uses its **existing brand colors** and a fully reinvented visual identity, with **NO recognizable styling from the previous Paper Trail build**.
- [ ] The **homepage keeps its concepts, functional cards and interactions, but has entirely new visual styling/composition**.
- [ ] **Every video remains exactly in its original location**, unchanged and working.
- [ ] **Existing and new photo library is examined and used across the site** where relevant; no stretching/blurry enlargements.
- [ ] Glow Rituals positive reference is reflected in **both the Notes listing cards and individual Notes reading pages**.
- [ ] Menu is genuinely redesigned and usable by mouse, touch and keyboard in all layouts and languages.
- [ ] Each page has its correct visible title/H1; Notes index is labeled **Notes**.
- [ ] Notes page has **no “8 articles” / article count labels** or standalone “Articles” category labels.
- [ ] No “Explore” calls to action; contextual “Read About [topic]” or “Read Article” links work.
- [ ] All peer cards and image frames have **consistent sizes**; generated photos are crisp, not stretched, inappropriately cropped or enlarged.
- [ ] White topic-specific icons over existing photos are cohesive and individually appropriate.
- [ ] Notes page doesn't resemble the supplied StartWeb7, Paradigm Janitorial or DommyDom listing layouts, and closely reflects the **Glow Rituals positive reference**.
- [ ] English plus all nine requested languages are selectable; **only Home + Notes listing** translated.
- [ ] The small **“Only the Home and Notes pages are available in this language.”** notice appears on both translated pages, with no English notice or intrusive banners.
- [ ] Small compliant **Google translation attribution/link** is at the bottom, never a large top Google box.
- [ ] Full Notes articles remain English and this is clear at translated listing links.
- [ ] Menu, links, cards, relevant page UI and chat interface follow selected language; Arabic/Farsi RTL work.
- [ ] Existing HubSpot leads are verified intact; do not falsely claim free-form multilingual AI if no real backend exists.
- [ ] Saved translations persist; visits make **zero Google Translation calls**.
- [ ] New/edited titles and previews translate once during approved publishing process, save automatically and are cache-safe.
- [ ] Shared usage accounts for DommyDom (6/day), StartWeb7 (3/day) and Paper Trail (3/day); $10/month ongoing target with fail-closed safeguards and honest billing limitations.
- [ ] Mock dry runs, responsive screenshots, performance/flash checks and link tests are complete.
- [ ] **No real API calls, deployment, commits, pushes, credential creation or paid changes before approval.**

**Do not treat this master brief as permission to invent missing code, photographs, services, translated full articles, HubSpot IDs, or billing settings. Verify actual files, build the system in safe stages, and surface blockers instead of guessing.**
