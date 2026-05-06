# HireAI Implemented Content Registry

Purpose: prevent Adriano/HireAI from reusing exact topics, hooks, captions, illustrations, or carousel concepts that have already been implemented.

Before any 9AM content generation or manual HireAI creative request, check this registry first. New concepts must be meaningfully different from the entries below unless Adriane explicitly asks to reuse/remix one.

## Status Legend

- `approved_sample` — approved ground truth/sample; do not regenerate as a “new” post.
- `implemented` — built/rendered in the repo; avoid duplicate topic/hook/illustrations.
- `dry_run_used` — used for automation testing; avoid using as a fresh daily post unless explicitly approved.
- `rejected_process` — output/process should not be repeated.
- `review_pending` — generated and posted for review, not approved/scheduled yet.

## Implemented / Used Content

### HR Onboarding / Repeated HR Questions Carousel v5

- **Status:** `approved_sample`, `dry_run_used`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** HR teams repeatedly answering leave balance, onboarding, document, and policy questions.
- **Primary hook:** “How many leave days do I have left?” / answered repeatedly by HR.
- **Caption/theme:** HR should not spend the week answering the same employee questions; HireAI handles repeat questions, reminders, and checklists so HR can focus on people.
- **Visual/illustration identifiers:** phone/chat volume, overflowing inbox/person at laptop, people vs paperwork, HR automation/resolution, CTA/footer band.
- **Repo references:**
  - `samples/creatives/hr-onboarding-carousel-v5/`
  - `samples/illustrations/hr-onboarding-carousel-v5/`
  - `examples/hr-onboarding/option-c-carousel.html`
  - `scripts/render-hr-onboarding-carousel.py`
- **Do not repeat as new:** same HR leave-days/onboarding FAQ angle, same exact caption, same exact v5 slides/illustrations.

### Dev/About Page Capability Carousel

- **Status:** `approved_sample`, `implemented`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** HireAI can add an About page to an existing website from one prompt while preserving the brand/design style.
- **Primary hook:** One prompt can turn into a matching, brand-aware website/page update.
- **Caption/theme:** HireAI understands existing design context and implements dev changes without starting from scratch.
- **Visual/illustration identifiers:** problem → prompt/send-message UI → matching style → finished About page result.
- **Repo references:**
  - `samples/creatives/dev-about-page-carousel-final/`
  - `samples/illustrations/dev-about-page-carousel-final/`
  - `scripts/render-dev-about-carousel.py`
- **Do not repeat as new:** exact About-page one-prompt storyline or same prompt/UI/result sequence.

### Content Production Bottleneck / Brief-Draft-Revise Carousel

- **Status:** `implemented`, `dry_run_used`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** Content production gets stuck in briefing, drafting, revising, and tone-correction loops.
- **Primary hook:** “Brief. Draft. Revise. Repeat.” / every piece of content costs time.
- **Caption/theme:** The bottleneck is the process; HireAI drafts on brief and keeps content work moving.
- **Visual/illustration identifiers:** loop graphic, time blocks, funnel/bottleneck, Johnny/document, Book discovery CTA.
- **Repo references:**
  - `examples/content-production/option-b-carousel.html`
  - `exports/content-production-option-b/`
  - `assets/generated/content-production-option-b/`
  - `scripts/render-content-production-carousel.py`
- **Do not repeat as new:** same Brief/Draft/Revise/Repeat hook, same time-cost breakdown, same bottleneck/process framing.

### Lead Handoff / Missed Follow-Up Carousel

- **Status:** `review_pending`, `dry_run_used`, `needs_style_revision`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** Leads and customer requests get lost during cross-tool handoffs between inbox, CRM, spreadsheets, calendar, and team ownership.
- **Primary hook:** “The lead didn’t ghost you. Your follow-up did.”
- **Caption/theme:** Missed opportunities start as tiny dropped handoffs; HireAI checks context, drafts replies, updates systems, and nudges the right owner.
- **Visual/illustration identifiers:** missed follow-up inbox/alarm/CRM card, handoff chaos across tools, AI workflow hub, clear owner/task board, CTA/footer band.
- **Repo references:**
  - `examples/lead-handoff/option-a-carousel.html`
  - `assets/generated/lead-handoff-dryrun/`
  - `exports/lead-handoff-dryrun/`
  - `scripts/render-lead-handoff-carousel.py`
- **Discord review thread:** `1501599616179765389`
- **Postiz:** not uploaded/scheduled; waiting for real human approval.
- **Revision note:** Adriane flagged that the generated illustrations do not sufficiently match prior uploaded HireAI illustration/creative art style. Before approval/scheduling, regenerate or revise illustrations using existing uploaded illustrations and approved creatives as style references.
- **Do not repeat as new:** exact missed-lead/follow-up hook, same handoff sequence, same caption structure, or same illustrations.

### Approval Flow / Stuck Decisions Carousel

- **Status:** `review_pending`, `dry_run_used`, `needs_layout_flow_revision`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** Work stalls because approvals float between chat, inbox, invoices, discounts, contracts, and team ownership.
- **Primary hook:** “The work isn’t blocked. The approval is.”
- **Caption/theme:** Teams waste time chasing decisions; HireAI checks context, finds the right approver, follows up, and records the decision.
- **Visual/illustration identifiers:** stuck approval request in chat/inbox, approval bottleneck pile, approval routing hub, resolved approvals dashboard/task board, CTA/footer band.
- **Repo references:**
  - `examples/approval-flow/option-a-carousel.html`
  - `assets/generated/approval-flow-daily/`
  - `exports/approval-flow-daily/`
  - `scripts/render-approval-flow-carousel.py`
- **Discord review thread:** `1501616649420144660`
- **Postiz:** not uploaded/scheduled; waiting for real human approval.
- **Revision note:** Adriane flagged that this run still did not properly use the accepted HTML/CSS layout flow; do not schedule as-is. Future attempt should use accepted layout references and browser-rendered HTML/CSS source composition, not a custom final-slide recreation.
- **Style references used:** existing uploaded HireAI illustrations and approved creatives from `samples/illustrations/hr-onboarding-carousel-v5/`, `reference-creatives/illustration-inspiration/sample-illustrations/`, and approved HR onboarding creative refs.
- **Do not repeat as new:** exact approval-blocked hook, same invoice/discount/contract approval chase framing, same caption structure, or same illustrations.

### Meeting Follow-Through / Notes to Next Actions Carousel

- **Status:** `implemented`, `posted_now`, `dry_run_used`
- **Format:** 4-slide 1080×1080 carousel
- **Core topic:** Meeting notes and decisions get lost because nobody turns them into owners, reminders, CRM updates, or task-board follow-through.
- **Primary hook:** “The meeting ended. The work didn’t.”
- **Caption/theme:** HireAI turns meeting notes into assigned next actions, routing tasks, owners, reminders, and updates across the tools the team already uses.
- **Visual/illustration identifiers:** video meeting with messy notes, scattered action items across chat/calendar/task list, automation hub routing notes into tasks, completed meeting follow-through board, CTA/footer band.
- **Repo references:**
  - `examples/meeting-to-tasks/option-a-carousel.html`
  - `assets/generated/meeting-to-tasks-html/`
  - `exports/meeting-to-tasks-html/`
- **Renderer:** browser screenshot from the accepted HTML/CSS source layout using Playwright; no custom PIL recreation for final slide composition.
- **Discord review thread:** `1501621025287307324`
- **Postiz:** posted immediately after human approval on 2026-05-07 00:29 Asia/Manila; verified in Postiz queue/state `QUEUE`.
  - Facebook Test Page (`cmou2ywk502jhns0y6d1eg2fu`): `cmou9vkom03sbl70ywne8rq76`
  - Instagram Standalone `hireaitest` (`cmou4lctp02u5ns0yk44wagrz`): `cmou9vkqc03scl70yz6flzb0a`
- **Style/layout references used:** existing uploaded HireAI illustration references from `samples/illustrations/hr-onboarding-carousel-v5/`, `reference-creatives/illustration-inspiration/sample-illustrations/`, accepted layout basis from `reference-creatives/layout-basis/overall-creatives/`, and the existing HTML/CSS carousel patterns in `examples/content-production/option-b-carousel.html` / `examples/hr-onboarding/option-c-carousel.html`.
- **Do not repeat as new:** exact meeting-ended/work-didn’t hook, same meeting-notes-to-tasks framing, same caption structure, or same illustrations.

### Tools Don’t Do the Work / People Do Dry Run

- **Status:** `rejected_process`, `dry_run_used`
- **Format:** 4-slide dry-run carousel generated outside the approved flow.
- **Core topic:** Businesses already have enough tools; the real problem is no one operates them consistently.
- **Primary hook:** “Your tools don’t do the work. People do.”
- **Caption/theme:** HireAI becomes the operator between business apps/tools.
- **Why flagged:** Dry run incorrectly used a one-off image-generation-heavy process instead of the existing HireAI HTML/CSS/preset workflow, and simulated human approval. Do not repeat this process.
- **Postiz test IDs:** Facebook `cmou5s83q031dl70yfu04zpx8`, Instagram `cmou5s85o031el70y49zquam6`; Adriane deleted the scheduled posts.
- **Do not repeat as new:** exact hook/caption or one-off process. If revisiting this concept, rebuild through the approved HTML/CSS workflow with a new angle and get real human approval.

## Generation Rule

For every future 9AM generation:

1. Read this registry before ideation.
2. Pick a concept not already represented here.
3. Avoid reusing exact captions, hooks, illustrations, CTA sequence, or slide structure from registered entries.
4. After a post is approved and implemented/scheduled, append a new registry entry with:
   - title/topic
   - status
   - hook
   - caption summary
   - visual identifiers
   - repo/output references
   - Postiz post IDs if scheduled
5. If a dry run or rejected process happens, record it too so future runs avoid repeating the mistake.
