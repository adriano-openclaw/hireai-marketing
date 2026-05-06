# HireAI Marketing

Marketing files, social creative assets, and reusable brand/design-system code for HireAI.

## Social Creative System

Reusable coded design assets for HireAI social media creatives.

## Current approved base background

- Canvas: `1080 x 1080px`
- Style: white background with subtle cool-gray circular dot pattern
- Approved use: default light background for future HireAI social media creative/design requests

## Files

- `light-background.html` — browser/CSS preview of the background pattern
- `generate-light-background.mjs` — deterministic Node.js PNG generator, no external dependencies
- `light-background-1080.png` — exported approved light background image

## Regenerate

```bash
node generate-light-background.mjs
```

This writes `light-background-1080.png`.


## Daily Postiz Automation

- `docs/postiz-daily-automation-flow.md` is the durable operating spec for the 9AM HireAI → Discord review thread → human approval → Postiz scheduling flow.
- `docs/9am-cron-step-by-step-flow.md` is the expanded exact checklist for the production-style 9AM cron creative flow.
- `/root/.openclaw/workspace/config/hireai-postiz-daily-flow.json` is the machine-readable config future cron jobs should load for the same flow.
- The daily job must stop at human review and must not simulate approval or upload/schedule to Postiz until a real human says `approved`, `post this`, or `schedule this`.
- The daily job must use the existing HireAI HTML/CSS/preset creative workflow, accepted layout references, and browser-rendered HTML/CSS output via `scripts/render-html-carousel.mjs`; it must not generate finished carousel slides as one-off whole-image outputs.

## Content Registry

- `content-registry.md` tracks implemented/used HireAI content concepts, hooks, captions, visual identifiers, sample references, and dry-run/rejected-process notes.
- Check it before generating new daily 9AM content or manual creative requests so Adriano/HireAI does not repeat existing posts.
- After a post is approved and implemented/scheduled, append it to the registry with its concept, hook, caption summary, visual identifiers, repo references, and Postiz IDs when applicable.

## Repository scope

This repo is intended to collect HireAI marketing assets over time, including social creatives, reusable backgrounds, generated images, caption drafts, brand rules, and future campaign files.
