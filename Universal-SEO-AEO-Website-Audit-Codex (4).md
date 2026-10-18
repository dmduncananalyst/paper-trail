# Universal SEO + AEO Website Audit — Codex Master Instructions

**Purpose:** Reuse these same instructions in **each individual website repository** (StartWeb7, DommyDom, Paradigm Janitorial, or Paradigm Security). Determine which business/site is currently open before starting. Never assume a domain, business type, page count, or location without verifying it.

## Non-negotiable: audit only, no site changes

Perform a **comprehensive page-by-page SEO, AEO (Answer Engine Optimization), technical SEO, indexing, local SEO, content, links, and off-page readiness audit**. This is a diagnostic task, **not an instruction to fix anything**.

- **DO NOT** rewrite content, change metadata, navigation, internal links, CSS, HTML, code, layouts, photographs, videos, article dates, page URLs, blog cards, schema, or site functionality.
- **DO NOT** commit, push, deploy, or publish. Do not alter the live website.
- You may create **only the three audit deliverable files** listed below inside the active project; keep any helper analysis scripts temporary and outside the repository where possible.
- Base your findings on this specific website, not generic SEO advice. Report **confirmed errors**, **external checks still needed**, and **optional improvements** as distinct classes. Never invent search rankings, backlinks, or Google indexing status.
- Audit *all* pages and articles, not just the homepage and a small sample. Distinguish actual failures from potential enhancements.

## 1. Website scope and complete page inventory

1. Identify the website structure, framework or static files, source routes, templates, navigation, known live domain and hosting configuration (where discoverable), and generated pages.
2. Inventory **every discoverable page**: homepage; about; services; detailed services; local city/neighborhood/service-area pages; categories; blog articles; category/blog index pages; portfolio/projects; contact/consultation; and other indexable content.
3. Document file path, canonical URL where determinable, type, indexability, sitemap presence, metadata, relevant internal linking, and page-specific issues.
4. Compare all known routes to navigational links and the XML sitemap. Identify duplicate routes, missing pages, orphaned pages, accidental noindex, broken destinations, and missing sitemap entries.
5. Count total pages and explain the inventory method and any coverage limitations. Do not assume all pages should be indexed.

## 2. Technical SEO and search engine access

Audit: robots.txt, XML sitemap validity and completeness, sitemap references, meta robots and X-Robots-Tag when inspectable, canonicals and canonical conflicts, HTTPS, domain/WWW and trailing-slash consistency, index-file duplication, redirect chains, 404s, broken internal/outbound links, page discoverability, orphan pages, duplicate content, crawlability and JavaScript-rendered content. Identify problems with image paths, accessibility of important links, pagination if applicable, and misconfigured generated routes. Do not treat a URL in a sitemap as proof Google has indexed it.

Evaluate mobile responsiveness, image dimensions/compression/formats and lazy loading, font loading, unnecessary scripts, layout shifts, Core Web Vitals opportunities, render-blocking requests, and accessibility issues that impair use or navigation. If you cannot actually run performance tests or access field data, do not invent scores. Explain what must be measured separately.

## 3. On-page SEO — every indexable URL

Review: unique, accurate SEO titles; meta descriptions; H1 and H2/H3 heading hierarchy; search intent alignment; topical focus; thin/duplicate/outdated content; confusing competing pages (keyword cannibalization); relevance to the exact services and locations; factual accuracy; effective internal linking and descriptive anchor text; contact/call-to-action clarity; image subject relevance, meaningful alt text, filenames, dimensions, and paths; author, publication and modified date consistency where applicable. Note which pages lack meaningful links to related services, cities, and articles.

Do not demand artificial title character limits or keyword stuffing. Recommend improvements only with evidence and preserve the existing writing pending explicit approval.

## 4. AEO / AI search readiness

Assess whether Google AI Overviews, ChatGPT Search, Perplexity, and other answer systems can find, understand and contextualize the website's useful content. Check: clear explanations of who the business serves and what it offers; direct but natural answers to relevant search intent; readable structure, headings, source attributions and verifiable facts; strong business identity/entity consistency; legitimate evidence of experience/expertise and trustworthiness; related-topic internal links; content freshness and topical coverage gaps.

Do not add forced question-format titles, speculative claims, unsupported FAQ schema, gimmicks, or promise rankings/AI citations. Evaluate the content as written and distinguish clarity issues from gaps.

## 5. Schema / structured data

Inventory existing JSON-LD and other schema. Validate type, properties, duplication, contradictions, incorrect URLs, and whether structured data matches visible content. Evaluate applicable Organization, LocalBusiness subtype, Service, Article/BlogPosting, BreadcrumbList, Person/author, and other **actually relevant** types. Flag errors or missing fields only where justified. Never suggest fake ratings, reviews, locations, or claims of automatic rich-result eligibility.

## 6. Local SEO when relevant

Check business name, published phone and location/service-area representation; city and neighborhood targeting; consistent local business identity; local service pages and their internal links; accurate addresses where genuinely public; local sources/citations; and Google Business Profile improvement opportunities. Do not assume the business has a storefront or make up addresses, review counts, service areas or local rankings. Identify which checks need access to Google Business Profile or live search data.

## 7. Backlinks, referring domains, and off-page optimization

Backlinks cannot be reliably audited from repository source code. Use reliable external backlink data **only when actually available**, name the source, and distinguish verified facts from unverified suggestions. Check true referring domains and anchor patterns, relevant local/industry mentions, broken incoming links, reputable citations, editorial/public relations opportunities, partnerships, and legitimate competitive opportunities. Do **not** fabricate referring domains, domain authority scores, backlink counts, or competitor rankings. Do not recommend buying spam links or bulk low-quality directory submissions.

## 8. Blog and editorial content

Audit **all** existing articles: indexability, category assignment, blog listing cards, title/excerpt uniqueness, photo matching and alt text, links to full articles, source and outbound links, relevant internal links to existing services/locations, related articles, article schema, author details where applicable, date consistency, duplicate topics, and content gaps. Preserve the **existing articles, dates, URLs, images, SEO metadata and card designs**. Report what might be improved later but do not change any of it now.

## 9. Google indexing, SEO performance, and external verification

Identify which questions require **live website access**, **Google Search Console** or **Google Business Profile**. If accessible, cite the actual source and date. Otherwise clearly label as not independently verifiable from code:

- Indexed, excluded, and submitted-but-not-indexed URL counts and reasons;
- Google Search Console sitemap submission/processing, crawl errors, URL Inspection results, coverage and manual actions;
- Organic queries, impressions, clicks, CTR, and average positions;
- Core Web Vitals real-user measurements, PageSpeed Insights and Lighthouse results;
- Actual backlinks, referring domains, and broken incoming links;
- Local visibility/profile data, business details and reviews where relevant.

Never claim a page is indexed merely because it exists or is in a sitemap. Never invent Google metrics, review counts, ranking positions, or external search outcomes. For review-count research use **Google Maps only** when those counts are necessary and obtainable; otherwise leave them unverified.

## 10. Report requirements — create exactly three files

Create these three files in the ROOT of the **currently open repository**. Do not edit any existing website file.

### `SEO-AEO-Master-Audit.md`

Comprehensive, clearly structured audit report with: website/project identified; methodology; number of pages/routes actually inspected and any limitations; inventory summary; technical/indexing findings; on-page findings; AEO/AI-search findings; schema problems; local SEO (if applicable); blog/content; images and performance; internal links; backlink/off-page checks; Google Search Console and other external checks not yet possible. For each issue provide **unique ID, Critical/High/Medium/Low priority, exact affected URL or source file, factual evidence, estimated impact, specific recommended repair, and how to verify it**. Split confirmed defects from questions requiring external evidence and optional opportunities. Finish with a concrete order of operations starting with crawl/index blockers.

### `SEO-AEO-Page-Inventory.csv`

A machine-readable CSV with **one row for EVERY page/route**, and columns at minimum:

`url_or_route,source_file,page_type,indexability,canonical,in_sitemap,seo_title_status,meta_description_status,h1_status,internal_link_status,schema_status,image_alt_status,content_findings,seo_priority,external_verification_needed`

Provide actual evidence or `unknown`/`not_checked`, never fabricate values. Make sure quoted cells and special characters are valid CSV.

### `SEO-AEO-Priority-Fix-List.csv`

A machine-readable, actionable **checklist** ordered from highest priority to lowest. At minimum:

`issue_id,priority,finding_type,affected_url_or_file,problem,evidence,recommended_fix,expected_benefit,verification_method,status`

Use `Critical`, `High`, `Medium`, or `Low`; `confirmed`, `requires_verification`, or `opportunity`; and status `Not Started` for every row. Each task should be specific enough to implement **later, only upon approval**. Avoid vague generic checklist items.

## Final acceptance criteria

1. The audit covers **the entire website**, not a selected handful of pages. Account for all discoverable routes and identify any exclusions or limitations.
2. Every substantive finding is **specific and evidenced**, not a generic SEO checklist.
3. The three audit deliverables are generated and easy to find in the currently open project.
4. Report risks and quick wins in descending importance; tell the user which external checks or permissions are necessary for a complete audit.
5. **DO NOT IMPLEMENT fixes** or change any current website content, visual layout, design, navigation, image, animation, URL, publication date, hosting/deployment setup, or functionality.
6. **DO NOT commit, push, or publish.** Briefly tell the user which files you created and the highest-priority findings, and await approval for any corrections.

**Reminder:** This is a universal prompt. Audit only the website in the currently open VS Code Explorer/repository. Do not accidentally audit or modify a different business's project.
