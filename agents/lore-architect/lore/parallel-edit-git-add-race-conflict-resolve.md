# Don't Parallelize Content Edit with `git add`/`commit` on Conflict Resolve

When resolving a merge conflict, issuing a file edit (StrReplace/Write) in the **same parallel
tool batch** as `git add` / `git commit` races: the add can stage the pre-edit file (still carrying
`<<<<<<<` / `=======` / `>>>>>>>` markers), and the commit lands conflict markers on the branch.

Confirmed 2026-07-27 merging `wip/lr-core-v31` → `main` in `lore-framework-dev`: the merge commit
carried markers in `trilens-loop-feature.md`; working tree looked clean after a parallel edit.
Follow-up commit `0112890` cleaned them. Signature: working tree clean of markers while
`git show HEAD:path` still shows them.

## Rule

Conflict resolve is strictly serial: edit → verify no markers in the file → `git add` →
`git commit`. Never batch the edit with the git write steps.

## Verify the committed blob

Before push (or immediately after a local merge commit), grep the **committed** path
(`git show HEAD:path`), not only the working tree. Same discipline as
`verify-before-acting-on-suspected-bugs.md` — confirm the artifact state you think you wrote.

## See Also

- `verify-before-acting-on-suspected-bugs.md` — parallel tool-call attribution; verify filesystem
  state before asserting a fix
- `v31-lr-core-parked-2026-07-25.md` — the merge this lesson came from
