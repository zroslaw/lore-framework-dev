---
lore: 1
type: topic
summary: "How to research OpenAI products from this workspace (2026-10-14): which sites block fetches, the llms-full exports and the split helper, Markdown twins, the plan matrix, the changelog, and how to weigh snippets."
parent: lore-context.md
---

# Research method for OpenAI docs

Learned on 2026-10-14 in the first full research pass. If a step fails, recheck the block or the
URL before you change the method.

## What blocks

- help.openai.com (all articles), chatgpt.com/pricing, and openai.com/chatgpt/pricing send an
  HTTP 403 challenge page. This occurs with WebFetch and with curl, also with a browser user agent.
- For these pages, use WebSearch result snippets. Label the fact "documented, via search snippet".
  Read the page in a browser before you quote a plan or a price from a snippet.

## What works

- curl works on developers.openai.com and learn.chatgpt.com. Every page has a Markdown twin:
  append `.md` to the URL.
- Whole-site exports:
  - https://learn.chatgpt.com/docs/llms-full.txt — all ChatGPT and Codex docs, about 2.3 MB.
  - https://developers.openai.com/plugins/llms-full.txt — the plugin and MCP developer docs.
- Download an export one time, split it into one file per page, then grep the files. This is much
  faster than a fetch for each page. The helper [`workdir/split-llms-full.py`](../workdir/split-llms-full.py)
  does the split: `python3 -I workdir/split-llms-full.py <llms-full.txt> <output-dir>`. In the
  exports, each page starts with a `---` line and then a `# Title` line. Keep the download and the
  output in a scratch directory, not in `workdir/`.
- **Plan matrix**: the raw https://learn.chatgpt.com/docs/pricing.md holds a
  `<CodexPlanFeatureMatrix>` component. The rendered export drops it. Parse the raw `.md` to get
  the availability for each plan.
- **Dated changes**: use the weekly digest https://learn.chatgpt.com/docs/whats-new. The changelog
  page (`/docs/changelog`) has no `.md` twin (HTTP 404). Its HTML is about 1.8 MB and only part of
  it is rendered on the server.
- **Codex CLI releases**: `gh api "repos/openai/codex/releases?per_page=8"`. Quote the URL in zsh,
  because zsh reads `?` as a glob character.

## How to weigh sources

- Search engines keep old page versions. Example: a snippet of the plugin quickstart had a
  "Developer mode" step that the live page does not have. Fetch the live developer page before you
  trust a snippet about it.
- Third-party pages that say "developer mode" or "connectors" describe the time before plugins
  (before about 2026-03 to 2026-07). Give them less weight than newer pages.

## Refresh order

1. The What's new digest — find what changed after the last check date.
2. The llms-full exports — split them and grep for the changed features.
3. Search snippets — only for help.openai.com and the pricing pages.

Then recheck the [open verification items](open-verification-items.md).
