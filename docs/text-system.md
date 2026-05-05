# HireAI Creative Text System

Purpose: reusable typography roles for HireAI social creatives. This defines how text should be styled when composing final creatives through HTML/CSS.

## Text roles

### `h1` / `.hireai-h1`

- Font: Fraunces — https://fonts.google.com/specimen/Fraunces
- Color: `#000000`
- Weight: bold / extra-bold; use CSS default `800` unless a specific layout needs `700`
- Role: biggest and most prominent text in the creative
- Typical Figma sizes seen: `64` or `80` (treat as px in CSS unless export testing suggests otherwise)
- CSS default: `80px`, tight line-height `0.95`, slight negative letter spacing

### `highlight` / `.hireai-highlight`

This is the named role for the previously unnamed orange handwritten text.

- Font: Caveat — https://fonts.google.com/specimen/Caveat
- Color: HireAI orange `#E85328`
- Weight: bold (`700`)
- Role: most important keyword or emotional/eye-catching word in the copy
- Size: depends on layout and relationship to h1/body text
- Usage: usually required with Fraunces in most creatives
- Optional modifier: `.hireai-highlight--underline` for orange handwritten underline emphasis
- Optional modifier: `.hireai-highlight--block` when the highlighted phrase should sit on its own line

### `body-bold` / `.hireai-body-bold`

- Font: Inter — https://fonts.google.com/specimen/Inter
- Color: `#000000`
- Weight: bold (`700`)
- Role: slightly longer descriptive text or supporting copy
- Size: layout-dependent; default token is `28px`
- Optional: only use when a creative needs explanatory copy

### `note` / `.hireai-note`

- Font: Inter — https://fonts.google.com/specimen/Inter
- Color: gray `#7C7C7C`
- Weight: regular (`400`)
- Role: small pieces of text, secondary notes, microcopy, small descriptors
- Size: layout-dependent; default token is `20px`
- Optional: only use when needed

## Usage principles

- Fraunces and Caveat are required in almost every text-based creative.
- Inter Bold and Inter Regular gray are optional and should only appear when the layout/content needs them.
- Use the exact SVG assets for HireAI logos; do not recreate logos as live Fraunces text.
- Text sizes are layout-dependent. Start from defaults, then tune per creative after rendering and visual inspection.
- The orange highlight should usually be the single most eye-catching keyword/phrase, not every keyword.
- Avoid clutter: one clear hierarchy beats several competing text blocks.

## Illustration overflow rule

Illustrations may go outside the 1080×1080 canvas bounds if it improves the design. This is allowed when the final cropped output looks intentional and clean.

Reference: `reference-creatives/layout-basis/overall-creatives/overall-layout-03-bullets-top-illustration-bottom.png`

## Required visual QA before delivery

Before sending any final HireAI creative:

1. Render/export the final image.
2. Inspect the rendered output visually.
3. Check for overlapping components, clipped important content, bad logo placement, crowded text, unreadable text, accidental readable text inside generated illustration screens/documents, or composition imbalance.
4. If there is a problem, fix and rerender before delivering.
5. Only then upload the preview to Discord and provide the GitHub raw HQ link.
