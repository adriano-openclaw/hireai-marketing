# 9AM HireAI Daily Creative Cron — Step-by-Step Flow

This is the exact production-style flow the daily 9:00 AM Asia/Manila cron job must follow.

## Cron Schedule

- **Time:** 9:00 AM
- **Timezone:** Asia/Manila
- **Cron expression:** `0 9 * * *`
- **OpenClaw job id:** `133f8d8d-7a96-43bc-bb7c-3da66b5fdf36`
- **OpenClaw flags:** use `--tz Asia/Manila --exact --session isolated`
- **Review channel:** Discord channel `1501561144039575572`
- **Approval phrases:** `approved`, `post this`, `schedule this`

## Registered OpenClaw Cron Job

Current installed job:

```bash
openclaw cron show 133f8d8d-7a96-43bc-bb7c-3da66b5fdf36
```

Expected critical fields:

- `name: HireAI daily creative review`
- `schedule: cron 0 9 * * * @ Asia/Manila (exact)`
- `session: isolated`
- `delivery: none -> discord:channel:1501561144039575572 (explicit)`
- `failure alert: discord:channel:1501365226937909288`
- `timeoutSeconds: 1800`

The job itself should send to the review channel using the Discord message tool. Runner fallback delivery is disabled to avoid duplicate final status posts.

## Non-Negotiable Rules

1. Do not reuse existing posts as new content.
2. Do not generate finished carousel slides as whole images.
3. Do not use a custom final-slide renderer that bypasses the accepted HTML/CSS layout flow.
4. Use image generation only for supporting illustration assets.
5. Use existing uploaded HireAI illustrations and approved creatives as style references before generating new illustration assets.
6. Use accepted HireAI HTML/CSS layout references as the source composition.
7. Render the final slides from browser screenshots of the HTML/CSS source.
8. Run visual QA before posting.
9. Post only to Discord review and stop.
10. Do not upload or schedule to Postiz until a real human approval phrase appears in the review thread.

## Full Daily Flow

### 1. Load the durable config and rules

Read:

- `/root/.openclaw/workspace/config/hireai-postiz-daily-flow.json`
- `docs/postiz-daily-automation-flow.md`
- `content-registry.md`
- `/root/.openclaw/workspace/skills/hireai-marketing/SKILL.md`

### 2. Check for duplicate content

Before ideation, inspect `content-registry.md` and reject any idea that repeats:

- same topic
- same primary hook
- same caption structure
- same slide sequence
- same illustration subjects
- same CTA sequence
- exact approved sample content

If a concept is already `review_pending`, `implemented`, `dry_run_used`, or `approved_sample`, do not use it as a fresh daily post unless Adriane explicitly asks.

### 3. Pick one new content idea

Generate one meaningfully new HireAI post idea.

Output internally:

- content idea
- primary hook
- caption draft
- four-slide message arc
- planned visual identifiers for each slide

### 4. Inspect style and layout references

Before generating illustrations, inspect existing references:

- `samples/illustrations/hr-onboarding-carousel-v5/`
- `samples/illustrations/dev-about-page-carousel-final/`
- `reference-creatives/illustration-inspiration/sample-illustrations/`
- `samples/creatives/hr-onboarding-carousel-v5/`
- `samples/creatives/dev-about-page-carousel-final/`
- `reference-creatives/layout-basis/overall-creatives/`
- `examples/hr-onboarding/option-c-carousel.html`
- `examples/content-production/option-b-carousel.html`
- `components/hireai-brand.css`

Style constraints to preserve:

- warm orange / peach / charcoal / white palette
- thick black rounded outlines
- flat editorial SaaS illustration style
- simple character proportions and UI shapes
- soft peach blobs where useful
- no photorealism, 3D, gradients, decorative palettes, logos, or readable generated text

Layout constraints to preserve:

- 1080×1080 canvas
- approved dotted white background
- top-left exact HireAI box logo
- top-right four-dot pagination with orange active dot
- approved Fraunces / Caveat / Inter typography roles
- exact HireAI wordmark placement when layout calls for it
- CTA/footer pattern from approved samples when needed
- generous safe margins and no text/illustration collisions

### 5. Generate only supporting illustration assets

Use image generation only for individual illustration assets.

When supported, pass existing uploaded HireAI illustration references into the image generation call.

Reject/regenerate any asset that has:

- noticeably different art style
- generated readable text
- logos or fake brand marks
- wrong palette
- 3D/photoreal/painterly appearance
- overly generic corporate-vector look

### 6. Compose final slides in accepted HTML/CSS

Create or update an HTML file under `examples/<campaign-slug>/`.

The HTML must be the source composition layer and must assemble:

- approved background
- exact logos
- pagination
- headline/body/highlight typography
- generated illustration assets
- CTA/footer if needed

Use existing accepted layouts as basis:

- `examples/hr-onboarding/option-c-carousel.html`
- `examples/content-production/option-b-carousel.html`
- `reference-creatives/layout-basis/overall-creatives/`

Do not hand-build the final composition directly in PIL/canvas unless it exactly renders the accepted HTML/CSS output. Browser-rendered HTML/CSS is the default final export path.

### 7. Render with browser screenshot

Use the reusable renderer:

```bash
npm run render:html-carousel -- examples/<campaign-slug>/<file>.html exports/<campaign-slug> <filename-prefix>
```

This calls:

```bash
node scripts/render-html-carousel.mjs <htmlPath> <outDir> [prefix]
```

Expected output:

- four `1080×1080` PNG files
- generated from the HTML/CSS source
- stored under `exports/<campaign-slug>/`

### 8. Visual QA gate

Before posting, inspect the four rendered slides against existing HireAI references.

QA must check:

- style continuity with existing uploaded illustrations
- accepted layout feel
- text legibility
- chrome/logo/pagination presence
- CTA/footer spacing
- illustration/text overlap
- clipping/crowding
- generated text/logos/artifacts
- whether Adriane would likely reject it

If any blocker appears, fix/regenerate/rerender before Discord.

### 9. Post clean Discord review thread

Create a new review thread in Discord channel `1501561144039575572`.

The thread message should look like a real production review, not a dry-run explanation.

Include only:

- title
- content idea
- caption draft
- note that 4 creatives are attached
- review instructions
- approval phrases

Then attach the four rendered PNG slides.

Do not include internal debugging text like “corrected dry run”, “this follows the intended flow”, or “does not simulate approval.”

### 10. Stop and wait for real human approval

After posting to Discord:

- do not upload to Postiz
- do not schedule
- do not simulate approval
- do not continue unless a real human replies with one approval phrase

Approval phrases:

- `approved`
- `post this`
- `schedule this`

### 11. Postiz handoff after approval only

After real approval:

1. Check Postiz queue for the current Asia/Manila day.
2. If today has existing/pending content, schedule the approved post at the next available slot.
3. If today is empty, schedule 3 hours after approval.
4. Upload only approved media to Postiz.
5. Use only whitelisted test integration IDs for now.
6. Verify the scheduled posts appear in queue.
7. Reply in the review thread with schedule time, destinations, Postiz IDs, and verification result.
8. Update `content-registry.md` with final status and Postiz IDs.

## Current Known Good Test

The first run that followed this corrected flow was:

- **Concept:** Meeting Follow-Through / Notes to Next Actions
- **Review thread:** `1501621025287307324`
- **HTML source:** `examples/meeting-to-tasks/option-a-carousel.html`
- **Output:** `exports/meeting-to-tasks-html/`
- **Renderer:** `scripts/render-html-carousel.mjs`
- **Postiz:** no writes; waiting for human approval

## Failure Modes to Avoid

- Reusing HR onboarding v5 as a “new” post.
- Reusing old captions/hooks already in `content-registry.md`.
- Generating full slides as single images.
- Using custom PIL/canvas final composition instead of accepted HTML/CSS source composition.
- Generating illustrations from text prompt alone when references exist.
- Posting off-style illustrations just because layout QA passed.
- Scheduling to Postiz before human approval.
