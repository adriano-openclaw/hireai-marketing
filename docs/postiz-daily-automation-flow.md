# HireAI × Postiz Daily Automation Flow

This is the durable operating spec for Adriano/HireAI daily content generation, Discord human review, and Postiz publishing.

For the fully expanded production checklist, use `docs/9am-cron-step-by-step-flow.md`.

## Current Principle

HireAI/Adriano is the marketing operator/brain. Postiz is the publishing and scheduling layer.

- **Adriano/HireAI:** brand memory, content strategy, caption writing, creative generation, Discord review loop, human revisions, approval detection, scheduling decision, registry updates.
- **Postiz:** connected social channels/integrations, media upload, post scheduling/publishing, queue state, analytics later.
- **API-first:** use Postiz Public API for deterministic automation.
- **MCP later:** optional operator mode for messy client-provided asset instructions, not the default automation backbone.

## Machine-Readable Config

Cron jobs and future automations should also read:

```text
/root/.openclaw/workspace/config/hireai-postiz-daily-flow.json
```

That file mirrors the key runtime values from this spec: review channel, approval phrases, content registry path, Postiz helper/env paths, allowed test integrations, approval delay, and no-simulated-approval guardrails.

## Fixed Runtime Settings

- **Daily generation time:** 9:00 AM Asia/Manila
- **Discord review channel:** `<#1501561144039575572>` / `1501561144039575572`
- **Approval phrases:** exactly:
  - `approved`
  - `post this`
  - `schedule this`
- **Postiz timezone:** `Asia/Manila`
- **Approval delay:** 3 hours
- **Postiz env file:** `/root/.openclaw/secrets/postiz.env`
- **Postiz API mode:** cloud
- **Current test integrations:**
  - Facebook Test Page: `cmou2ywk502jhns0y6d1eg2fu`
  - Instagram Standalone `hireaitest`: `cmou4lctp02u5ns0yk44wagrz`
- **Allowed integration env:** `POSTIZ_ALLOWED_INTEGRATION_IDS=cmou2ywk502jhns0y6d1eg2fu,cmou4lctp02u5ns0yk44wagrz`

Never print or expose the Postiz API key.

## Mandatory Pre-Generation Checks

Before any 9AM generation or manual HireAI content request:

1. Read `content-registry.md`.
2. Avoid duplicate concepts, hooks, captions, slide structures, visual identifiers, and exact illustrations.
3. Use approved samples as design ground truth, not as fresh daily content.
4. If reusing/remixing an existing concept, only do so when Adriane explicitly asks.

## Mandatory Creative Production Flow

Do not generate the finished creative as one whole image.

The approved HireAI flow is:

1. Generate or select a meaningfully new content idea.
2. Write caption draft.
3. Generate supporting illustration assets only when needed.
   - Before generating, inspect existing uploaded HireAI illustration references and approved creatives.
   - Use those images as concrete style references/inspiration for the prompt and, where the image tool supports it, as reference images.
   - The generated illustration style must match the existing HireAI sample feel: warm orange/peach/charcoal palette, rounded editorial SaaS shapes, soft shadows, similar line/shape language, and similar character/UI proportions.
   - If the generated art style noticeably diverges from prior uploaded illustrations/creatives, treat it as a QA failure and regenerate before posting.
4. Use the existing HireAI repo system and accepted layout references:
   - approved background
   - exact logo assets
   - approved typography rules
   - pagination
   - CTA/footer patterns when appropriate
   - HTML/CSS composition / existing renderer patterns
   - accepted layout references under `reference-creatives/layout-basis/overall-creatives/`
   - existing HTML/CSS carousel examples as the composition basis
5. Render four square creatives, 1080×1080 from browser screenshots of the HTML/CSS source using `scripts/render-html-carousel.mjs` / `npm run render:html-carousel`.
6. Run visual QA before posting to Discord.
7. QA must include style-continuity against existing uploaded illustrations and approved creatives, not only layout/legibility.
8. If QA finds obvious issues or art-style drift, fix/regenerate before posting.

Current source of truth references:

- `samples/creatives/hr-onboarding-carousel-v5/`
- `samples/illustrations/hr-onboarding-carousel-v5/`
- `samples/creatives/dev-about-page-carousel-final/`
- `samples/illustrations/dev-about-page-carousel-final/`
- `examples/hr-onboarding/option-c-carousel.html`
- `examples/content-production/option-b-carousel.html`
- `scripts/render-hr-onboarding-carousel.py`
- `scripts/render-content-production-carousel.py`
- `scripts/render-html-carousel.mjs`
- `components/hireai-brand.css`

## 9AM Cron Behavior

At 9:00 AM Asia/Manila, the cron/job should:

1. Check `content-registry.md`.
2. Generate one new content idea.
3. Write one caption draft.
4. Create four 1080×1080 creatives through the approved HTML/CSS/preset workflow.
5. Run visual QA.
6. Send the package to Discord review channel `1501561144039575572`.
7. Create a new thread for that day’s post.
8. Attach:
   - content idea
   - caption draft
   - four creatives
   - QA notes
   - clear review instructions
   - approval phrases
9. Stop and wait for real human review.

The 9AM job must **not**:

- simulate approval
- upload to Postiz automatically
- schedule/post without a real approval phrase
- reuse exact existing content from `content-registry.md`
- generate finished creatives as a single image-generation output

## Human Review Loop

Humans can reply in the review thread with:

- caption changes
- creative changes
- layout/design changes
- regenerate requests
- approval phrase

Adriano/HireAI should revise within the same review thread until a human uses one approval phrase.

Only the phrases below trigger Postiz handoff:

- `approved`
- `post this`
- `schedule this`

The trigger must come from an actual human message, not from Adriano simulating a user.

## Postiz Handoff After Approval

After a real approval phrase:

1. Check Postiz queue for the current Asia/Manila day.
2. If any existing/pending content is scheduled for today:
   - schedule the approved post at Postiz’s next available slot.
3. If no content is scheduled/pending today:
   - schedule/post the approved post 3 hours after the approval time.
4. Upload approved media to Postiz.
5. Create/schedule the post only for whitelisted integration IDs.
6. Verify the scheduled posts appear in Postiz queue with state `QUEUE` or equivalent.
7. Reply in the Discord review thread with:
   - scheduled destinations
   - scheduled date/time in Asia/Manila
   - Postiz post IDs
   - verification result
8. Append the final implemented/scheduled post to `content-registry.md`.

## Current Postiz Helper

Local helper script:

```bash
/root/.openclaw/workspace/scripts/postiz-helper.mjs
```

Available checks:

```bash
node scripts/postiz-helper.mjs check
node scripts/postiz-helper.mjs integrations
node scripts/postiz-helper.mjs today [YYYY-MM-DD]
node scripts/postiz-helper.mjs next-slot <integrationId>
node scripts/postiz-helper.mjs upload <filePath> --confirm-postiz-write
```

Upload is a Postiz write and requires explicit `--confirm-postiz-write`.

## Known Corrections / Lessons

- Do not reuse the HR onboarding carousel as a new daily post; it already exists as approved v5 ground truth.
- Do not use exact existing sample content/captions/illustrations for fresh 9AM content.
- Do not simulate human approval in dry runs or cron runs.
- Do not skip the existing HireAI HTML/CSS/preset composition workflow or accepted layout references.
- Image generation is for supporting illustrations, not whole finished carousel slides.
- Do not generate illustrations from text prompt alone when existing uploaded illustration/creative references are available; use those references for visual inspiration and reject outputs whose art style drifts from the prior HireAI set.
- Update `content-registry.md` after every approved/scheduled post or notable rejected/dry-run content.

## Manual Dry Run Modes

### Realistic dry run

Use this when testing the 9AM job behavior:

- generate/post to Discord review thread
- stop at human review
- no simulated approval
- no Postiz write

### Full Postiz write test

Use only when Adriane explicitly asks to test upload/scheduling:

- still create review thread first
- still wait for real approval unless Adriane explicitly says to proceed with a test write
- upload/schedule only to test integrations
- verify queue
- record result in `content-registry.md`
