When a design or implementation needs a **volatile external fact** — a current dollar price, rate limit, model ID, quota — fetch it from the authoritative live source at build time and cite the source URL + fetch date in a code comment. Do **not** rely on remembered/memorized figures, even when confident about them.

"I'm fairly confident I remember this number" is not the same bar as "I can point at where this number currently lives." For any fact an external party can change without this codebase's knowledge, do the live lookup and leave a dated citation. Treat **"couldn't verify" as a legitimate reason to mark a value `unavailable`/`unknown`** rather than ship an unverified guess.

## The concrete instance (session-usage cost feature)

Building the cost-computation feature, the design initially planned to source a Claude model pricing table from a bundled reference skill. That skill turned out to have a confirmed price for only **one** model (Fable 5) — Sonnet 5 / Opus 4.8 / Haiku 4.5 prices were not actually in it. Hardcoding remembered numbers for those would have been exactly the silent-fabrication the same design was explicitly refusing to do for other engines (Codex/Cursor cost, marked `unavailable` rather than guessed).

Caught by trying to **verify the source before writing the table**, not by assuming memory was good enough. Fetched the live pricing page (`platform.claude.com/docs/en/about-claude/pricing`), got exact current figures including an active introductory-pricing window with a documented expiry, and cited the fetch date in the resulting `PRICING` table comment so a future maintainer knows when to refresh it.

## Generalizable rule

Volatile external facts get a live lookup + a dated citation at the point of use; unverifiable ones get marked unavailable, never guessed. The citation is what makes the value maintainable — it tells the next maintainer *when* the number was true and *where* to re-check it.

## See Also

- `graduated-verification-confidence.md` — the "unavailable/unknown is a first-class outcome, not a failure to hide" principle; this applies it to external volatile facts specifically.
- `verify-before-acting-on-suspected-bugs.md` — the sibling reflex: confirm state directly before acting on it. This is the build-time analog (confirm the fact before hardcoding it).
- `naming-foundational-principles.md` — the meta-rule that a recurring, cleanly-stated lesson deserves its own named topic.
