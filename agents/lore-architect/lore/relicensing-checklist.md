---
lore: 1
type: topic
summary: "Changing the framework license (MIT, MIT-0 and back, 2026-10-06): the six sites that must move together, why it is not a VERSION release, the authorship check before push, and why push is the irreversible step."
parent: lore/versioning-release-types.md
---

Changing the framework's license (done 2026-10-06: MIT -> MIT-0, then back to MIT at the user's request).

**Sites that state the license** in `lore-framework/` — six places, all must move together: `LICENSE`, the `license` field in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json` and `.codex-plugin/plugin.json`, the `License:` line in `MARKETPLACE.md`, and the license link in `README.md`. Find them with `grep -rIn 'MIT'` and filter out commit/limit/permit noise. MIT-0's SPDX id is `MIT-0`; its text is MIT minus the "subject to the following conditions" notice requirement.

**No VERSION bump.** A license change is not a framework release: no migration, no release notes, no manifest `1.<VERSION>.0` bump. The user said so explicitly; the manifests are edited only in their `license` field.

**Pre-push check — authorship.** Run `git -C <repo> shortlog -sn HEAD` (the `HEAD` matters: without a revision, shortlog in a non-tty shell reads stdin and prints nothing). A foreign author with a substantive commit means relicensing needs their consent. **A second git identity can be the user's own** (here the "other contributor" was the user committing through a family member's account), so ask rather than assume either way. Holding the push until the user confirmed cost one turn and settled it.

**Push is the irreversible step.** A license grant can't be recalled: whoever clones in the window keeps those rights to that snapshot. Commit locally, confirm, then push. Reverting is a plain `git revert` (amend the message), pushed as a new commit; never rewrite published history.

**Third-party code** keeps its own license regardless.

See also [plugin-manifest-versioning.md](plugin-manifest-versioning.md) for the normal `1.<VERSION>.0` manifest bump that a license change deliberately skips.
