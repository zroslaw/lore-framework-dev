---
lore: 1
type: topic
summary: "A deny-list must exempt the operations that reduce the exposure it guards against — for a commit filter, every deletion — and the exemption must be keyed on the operation, not on one encoding of it."
parent: lore-context.md
---

# A Guard Must Not Block the Operation That Removes What It Guards Against

`/lr:workspace-sync` holds credential-shaped filenames back from a commit. Applied naively, the
same rule refused `git rm --cached .env` — the exact operation that removes a leaked credential
from the shared remote — and told the user "publish it deliberately if it belongs here", which is
nonsense addressed to somebody who has already decided. The credential stayed tracked; the guard
preserved the thing it existed to prevent.

**Rule: before shipping a deny-list, enumerate the operations that *reduce* exposure and exempt
them.** For a commit filter, every deletion is such an operation, for every hold reason, without
exception — the file is going away, so nothing the hold objects to can reach anyone.

Two follow-on traps, both hit in the same feature:

- **Key the exemption on the operation, not on one encoding of it.** Exempting status code `D`
  missed renames: `git mv credentials.json config.json` emits two `R` records, so the origin was
  still held, the new (innocuous) name was published, and the repo was left permanently dirty with
  a staged deletion nothing would finish — and the heuristic was then defeatable by a plain rename.
  Fix at the parse layer (emit a rename's origin *as* a deletion) so every consumer of the rule
  inherits it.
- **A copy's source is not a deletion.** `R` and `C` look alike in porcelain and are opposites
  here.

Sibling of [one-question-one-code-path.md](one-question-one-code-path.md): the guard and the remedy
must not disagree about what the dangerous state is. Feature context:
[workspace-sync-feature.md](workspace-sync-feature.md).
