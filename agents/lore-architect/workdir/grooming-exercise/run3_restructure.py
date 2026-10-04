import os
L='lore/'
ctx=open('lore-context.md').read()
secs={}
def take(name,start,end):
    global ctx
    a=ctx.index(start); b=ctx.index(end,a+1)
    secs.setdefault(name,[]).append(ctx[a:b].rstrip()+"\n"); ctx=ctx[:a]+ctx[b:]
G="gates-and-review-discipline"; E="executable-prose-and-design-checks"; S="git-and-state-safety"; F="user-feedback-working-style"
take(G,"- **Gates: cheapest-first","- **When a procedure doesn't execute")
take(E,"- **When a procedure doesn't execute","- **When TriLens is requested")
take(G,"- **When TriLens is requested","- **A gate result belongs")
take(G,"- **A gate result belongs","- **Three gate dispositions")
take(G,"- **Three gate dispositions","- **A gate cannot be a model self-report")
take(G,"- **A gate cannot be a model self-report","- **A failure list is a hypothesis")
take(G,"- **A failure list is a hypothesis","- **Decide where the guardrail lives")
take(E,"- **Decide where the guardrail lives","- **Verify before asserting")
take(E,"- **Design-time checks:**","- **Git safety in automatic paths.**")
take(S,"- **Git safety in automatic paths.**","- **Curation meta-rules:")
take(F,"- **User-feedback working style:**","## Key Constraints")
members={
G:"""a-gate-cannot-be-a-model-self-report a-gate-that-died-is-not-a-gate gate-waiver-is-a-record blast-radius-audit-when-a-gate-is-waived post-convergence-edits-need-their-own-gate defects-hide-in-the-intersections-a-suite-partitions dont-borrow-gate-vocabulary-for-non-gates non-convergence-diagnose-before-reviewing-again tiering-a-reviewed-spec-creates-unreviewed-seams a-detection-tier-must-outlive-the-cure-it-measures a-fix-is-a-change-and-changes-need-review a-fix-s-regression-test-misses-the-branch-the-fix-added fix-defects-are-context-errors lens-novelty-is-the-scarce-resource-on-re-review review-grounding-beats-lens-novelty settle-conflicting-reviewer-claims-in-the-source parallel-reviewer-fanout-pattern trilens-loop-feature ai-installer-review-lens a-release-record-goes-stale-while-you-fix-it a-release-review-starts-with-git-status prove-a-new-test-red-against-the-previous-tag a-red-test-may-be-asserting-a-true-fact measurement-records-name-their-environment execution-testing-catches-blind-ambiguity a-demo-must-test-the-state-it-leaves-behind a-new-command-inherits-its-neighbours-published-promises a-negative-grep-proves-the-pattern-absent a-displayed-attribute-can-have-more-than-one-source verify-before-acting-on-suspected-bugs lifecycle-testing-harness""".split(),
E:"""required-literal-output-is-what-models-drop the-terminal-step-is-the-step-that-gets-dropped instruction-location-beats-emphasis-in-long-docs models-copy-what-they-should-compute appended-docstring-step-must-match-execution-position step-number-cross-references-fail-silently adding-a-write-means-updating-the-approval-gate per-site-authoring-is-not-duplication single-canonical-source-discipline one-question-one-code-path short-circuit-on-the-condition-not-a-proxy classification-tables-enumerate-exit-paths-not-interesting-cases an-optional-step-must-fail-back-to-baseline scripted-prose-edit-needs-a-read-back self-documenting-payload-vs-heading-delimiters widening-a-source-drops-its-validation a-change-set-is-wider-than-its-diff a-rate-floor-is-wrong-in-both-directions guarding-on-a-normal-state-excludes-what-matters-most consistency-sweep-read-not-just-grep""".split(),
S:"""git-common-dir-for-repo-wide-state git-dash-c-needs-toplevel-guard git-ff-only-is-file-granular dont-autostash-it-reports-success-while-corrupting commit-before-fetch-makes-a-merge-recoverable relative-git-refs-retarget-when-a-procedure-moves-head prove-superseded-before-discarding-colliding-wip fold-feature-into-local-main-via-stash a-state-file-is-a-hint-not-a-verdict a-reported-error-is-not-proof-the-file-survived a-guard-must-not-block-its-own-remedy lock-claim-directory-creation-vs-contention macos-var-symlink-realpath-ambiguity realpath-for-identity-logical-for-contract-shape live-system-state-validate-on-a-copy-first name-keyed-global-registry-cannot-answer-per-scope release-commit-hash-from-tag committed-artifacts-carry-relative-paths lore-repo-divergence-is-self-inflicted sidecar-publish-rejected""".split(),
F:sorted(f[:-3] for f in os.listdir(L) if f.startswith('feedback-')),
}
lifecycle="lifecycle-harness-exit-code-is-not-a-verdict lifecycle-harness-plugin-identity-unverified unittest-k-is-substring-not-pytest transcript-vs-final-message-assertions triage-a-red-module-against-its-own-history run-duration-is-the-first-triage-signal".split()
info={G:("Gates and Review Discipline","How I gate, review and record a ship: cheapest-first gates, the three dispositions, TriLens judgement, artifact-state ownership, and why a gate is never a model self-report."),
E:("Executable Prose and Design Checks","Why procedures fail to execute and what to change (structure, not wording), plus design-time checks for guards, approval gates, intervals and optional steps."),
S:("Git and State Safety","Rules for git operations and state files in automatic paths: ff-only granularity, no autostash, common-dir vs worktree state, hint-not-verdict state files, atomic writes and path identity."),
F:("User Feedback Working Style","How the user wants me to work: recommend before asking, draft only on trigger, minimalism, small fail-closed guards, best-role-fit hosts. One topic per piece of feedback.")}
def setparent(name,newp):
    p=L+name+'.md'; s=open(p).read(); assert s.startswith('---\nlore: 1'),name
    head,rest=s.split('\n---\n',1)
    if '\nparent: '+newp in head: return
    assert '\nparent: lore-context.md' in head or '\nparent: lore/' in head,(name,head)
    import re
    head=re.sub(r'\nparent: .*','\nparent: '+newp,head,1)
    open(p,'w').write(head+'\n---\n'+rest)
for h,(title,summ) in info.items():
    for m in members[h]:
        assert os.path.exists(L+m+'.md'),m
        if m=='lifecycle-testing-harness': continue
        setparent(m,'lore/'+h+'.md')
    body='\n'.join(secs.get(h,[]))
    mem='\n'.join(f'- [{m}.md]({m}.md)' for m in members[h])
    intro={G:"The essential rules live below (moved here from `lore-context.md`); each rule's full body is in the member topics.",
           E:"Rules for writing procedures an executor will actually follow, and for designing guards that don't fail in the intersections. Moved from `lore-context.md`; bodies live in the members.",
           S:"Git and state-file safety for automatic paths. Moved from `lore-context.md`; bodies live in the members.",
           F:"One topic per piece of user feedback; the standing summary is below."}[h]
    assert len(summ)<=240
    open(L+h+'.md','w').write(f'---\nlore: 1\ntype: area\nsummary: "{summ}"\nparent: lore-context.md\n---\n\n# {title}\n\n{intro}\n\n'+(f'## Standing rules\n\n{body}\n' if body else '')+f'## Members\n\n{mem}\n')
p=L+'lifecycle-testing-harness.md'; s=open(p).read()
s=s.replace('type: topic','type: area',1); s=s.replace('parent: lore-context.md','parent: lore/'+G+'.md',1); open(p,'w').write(s)
for m in lifecycle: setparent(m,'lore/lifecycle-testing-harness.md')
ptr="""- **Gates, review and ship records** — cheapest-first gates (deterministic tests → `/lr:check` → dogfood → lifecycle suite and TriLens only on request); every gate is named *passed*, *waived* or *did not run* in the release notes before lore; a gate result belongs to one artifact state; a gate is never a model self-report; a failure list is a hypothesis until the transcripts are read. Hub: `gates-and-review-discipline.md`.
- **Executable prose and design checks** — when a procedure doesn't execute, change structure, not wording (required literal output, the terminal step, location, copy-vs-compute); decide where the guardrail lives; design-time checks on guards, intervals and optional steps. Hub: `executable-prose-and-design-checks.md`.
- **Git and state safety in automatic paths** — `--ff-only` is file-granular; never autostash, stash, force or reset; state files are hints, not verdicts; commit before fetch. Hub: `git-and-state-safety.md`.
"""
a=ctx.index("- **Verify before asserting**"); ctx=ctx[:a]+ptr+ctx[a:]
fb="- **User-feedback working style:** recommend before asking, draft only when triggered, \"acknowledge\" means do not act, minimalism, small fail-closed guards. Hub: `user-feedback-working-style.md`.\n\n"
a=ctx.index("## Key Constraints"); ctx=ctx[:a]+fb+ctx[a:]
open('lore-context.md','w').write(ctx)
print({k:len(v) for k,v in members.items()})
