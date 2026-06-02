export const meta = {
  name: 'lr-dev-file-quality',
  description: 'Analyze a single file for bugs and missing test coverage. Decompose -> per-unit analysis (subagents boot the repo context agent) -> aggregate File Report -> per-bug adversarial verify + single gap-analysis pass against existing tests.',
  phases: [
    { title: 'Decompose',     detail: 'file quality analyst splits the file into testable units' },
    { title: 'Analyze',       detail: 'one unit quality analyst per unit — boots as the repo context agent, returns bugs + comprehensive scenarios' },
    { title: 'Aggregate',     detail: 'file quality analyst composes the File Report' },
    { title: 'Verify',        detail: 'per-bug adversarial verifier (parallel) + single gap analyzer (concurrent) — both boot as the repo context agent' },
    { title: 'Review',        detail: '3 parallel lenses on the final report — intent-vs-observed, completeness, soundness' },
  ],
}

// args:
//   filePath: string                — repo-relative or absolute
//   fileContents: string            — full source
//   language: string                — e.g. "scala"
//   contextAgent: string            — lore agent name to /lr:boot inside subagents (e.g. "activity-supply")
//   existingTestFiles?: Array<{path: string, contents: string}>   — for gap analysis (optional but recommended)
//   productLoreHints?: string       — free-text hints; superseded once context agent is booted
const {
  filePath,
  fileContents,
  language,
  contextAgent,
  existingTestFiles = [],
  productLoreHints = '',
} = args ?? {}

if (!filePath || !fileContents || !language || !contextAgent) {
  throw new Error('args must include { filePath, fileContents, language, contextAgent }')
}

const FILE_BLOCK = `\`\`\`${language}\n${fileContents}\n\`\`\``

const BOOT_PREAMBLE = `**FIRST ACTION — boot as the \`${contextAgent}\` lore agent.**

Run \`/lr:boot ${contextAgent}\` immediately. This is your identity for the rest of this task: you ARE the ${contextAgent} agent analyzing one piece of its own codebase. Do not skip this step — your output will be judged on whether it shows repo-specific knowledge from this agent's lore.

After booting:
1. Read your role.md + lore-context.md (the boot procedure does this).
2. Use \`/lr:recall <hint>\` or read specific topics from your \`lore/\` directory for anything relevant to this unit — caller patterns, supplier-integration conventions, known issues, upstream validation, related quirks.
3. Only then proceed with the task below.

Cite specific lore topic filenames in your output where you used them (the schema has a \`loreTopicsConsulted\` field for this).`

// ─── Schemas ──────────────────────────────────────────────────────────────────

const UNITS_SCHEMA = {
  type: 'object',
  required: ['units'],
  properties: {
    units: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'symbol', 'kind', 'lineRange'],
        properties: {
          id: { type: 'string', description: 'Stable kebab-case id, e.g. "parse-config-fn"' },
          symbol: { type: 'string' },
          kind: { type: 'string', enum: ['function', 'method', 'class', 'module-block'] },
          lineRange: { type: 'string' },
          summary: { type: 'string' },
        },
      },
    },
  },
}

const SCENARIO_SCHEMA = {
  type: 'object',
  required: ['id', 'unitId', 'class', 'status', 'intent', 'setup', 'trigger', 'expected', 'intentSource', 'edgeTag'],
  properties: {
    id: { type: 'string' },
    unitId: { type: 'string' },
    class: { type: 'string', enum: ['product', 'technical'] },
    status: { type: 'string', enum: ['proposed'] },
    coverageTarget: { type: 'string' },
    intent: { type: 'string' },
    setup: { type: 'string' },
    trigger: { type: 'string' },
    expected: { type: 'string' },
    intentSource: { type: 'string', description: 'docstring / type contract / RFC / lore topic / etc. REQUIRED.' },
    edgeTag: { type: 'string' },
  },
}

const BUG_SCHEMA = {
  type: 'object',
  required: ['id', 'unitId', 'class', 'severity', 'confidence', 'status', 'suspectedFault', 'triggeringPath', 'expectedVsActual', 'intentSource', 'evidence'],
  properties: {
    id: { type: 'string' },
    unitId: { type: 'string' },
    class: { type: 'string', enum: ['product', 'technical'] },
    severity: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
    status: { type: 'string', enum: ['unreviewed'] },
    suspectedFault: { type: 'string' },
    triggeringPath: { type: 'string' },
    expectedVsActual: { type: 'string' },
    intentSource: { type: 'string' },
    evidence: { type: 'string' },
  },
}

const UNIT_REPORT_SCHEMA = {
  type: 'object',
  required: ['unitId', 'bugs', 'scenarios'],
  properties: {
    unitId: { type: 'string' },
    bugs: { type: 'array', items: BUG_SCHEMA },
    scenarios: { type: 'array', items: SCENARIO_SCHEMA },
    loreTopicsConsulted: { type: 'array', items: { type: 'string' }, description: 'Lore topic filenames the analyzer cited from its booted lore' },
  },
}

const FILE_REPORT_SCHEMA = {
  type: 'object',
  required: ['filePath', 'language', 'unitsAnalyzed', 'summary', 'perUnit'],
  properties: {
    filePath: { type: 'string' },
    language: { type: 'string' },
    unitsAnalyzed: { type: 'integer' },
    summary: {
      type: 'object',
      required: ['bugCounts', 'scenarioCounts'],
      properties: {
        bugCounts: { type: 'object' },
        scenarioCounts: { type: 'object' },
      },
    },
    perUnit: {
      type: 'array',
      items: {
        type: 'object',
        required: ['unitId', 'bugs', 'scenarios'],
        properties: {
          unitId: { type: 'string' },
          bugs: { type: 'array' },
          scenarios: { type: 'array' },
        },
      },
    },
    notes: { type: 'string' },
  },
}

const BUG_VERDICT_SCHEMA = {
  type: 'object',
  required: ['bugId', 'verdict', 'reasoning'],
  properties: {
    bugId: { type: 'string' },
    verdict: { type: 'string', enum: ['real', 'false-positive', 'inconclusive'] },
    confidenceAdjustment: { type: 'string', enum: ['raise', 'lower', 'unchanged'] },
    reachabilityCheck: { type: 'string', description: 'Is the triggering path actually reachable given repo usage?' },
    intentCheck: { type: 'string', description: 'Does the cited intent source actually say what is claimed?' },
    reasoning: { type: 'string' },
    loreTopicsConsulted: { type: 'array', items: { type: 'string' } },
  },
}

const GAP_ANALYSIS_SCHEMA = {
  type: 'object',
  required: ['extractedScenarios', 'matches', 'gaps', 'summary'],
  properties: {
    extractedScenarios: {
      type: 'array',
      items: SCENARIO_SCHEMA,
      description: 'Scenarios reverse-extracted from existing test files using the same Scenario schema',
    },
    matches: {
      type: 'array',
      items: {
        type: 'object',
        required: ['proposedId', 'matchedExistingId', 'matchKind'],
        properties: {
          proposedId: { type: 'string' },
          matchedExistingId: { type: 'string' },
          matchKind: { type: 'string', enum: ['exact', 'equivalent', 'partial'] },
          rationale: { type: 'string' },
        },
      },
    },
    gaps: {
      type: 'array',
      items: {
        type: 'object',
        required: ['proposedId', 'why'],
        properties: {
          proposedId: { type: 'string' },
          why: { type: 'string', description: 'Why no existing test covers this proposed scenario' },
        },
      },
    },
    summary: {
      type: 'object',
      required: ['proposedTotal', 'existingTotal', 'matchedCount', 'gapCount'],
      properties: {
        proposedTotal: { type: 'integer' },
        existingTotal: { type: 'integer' },
        matchedCount: { type: 'integer' },
        gapCount: { type: 'integer' },
        coverageRatio: { type: 'string', description: 'matched / proposed, as a string like "11/19"' },
      },
    },
    loreTopicsConsulted: { type: 'array', items: { type: 'string' } },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['lens', 'findings'],
  properties: {
    lens: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['target', 'issue', 'severity'],
        properties: {
          target: { type: 'string' },
          issue: { type: 'string' },
          severity: { type: 'string', enum: ['nit', 'minor', 'major'] },
        },
      },
    },
  },
}

// ─── Phase 1: Decompose ──────────────────────────────────────────────────────

phase('Decompose')

const decomposition = await agent(
  `You are the **file quality analyst** for the lr-dev framework.

Decompose the following ${language} file into testable **units** (functions, methods, classes, top-level blocks).
File: ${filePath}

${FILE_BLOCK}

Return a list of units. Each unit gets a stable kebab-case id, the symbol name, kind, line range, and a one-line summary. Group trivial getters/setters/boilerplate. Aim for the granularity at which a single test scenario would target one unit.`,
  { label: 'decompose', phase: 'Decompose', schema: UNITS_SCHEMA }
)

const units = decomposition.units
log(`Decomposed ${filePath} into ${units.length} unit(s)`)

// ─── Phase 2: Analyze (per unit, parallel) ───────────────────────────────────

phase('Analyze')

const unitReports = await parallel(units.map(unit => () => agent(
  `${BOOT_PREAMBLE}

---

You are a **unit quality analyst** (ephemeral). Two tasks at once for the unit below.

File: ${filePath}
Unit: ${unit.symbol} (${unit.kind}, lines ${unit.lineRange}) — ${unit.summary ?? ''}

Full file for context:
${FILE_BLOCK}

${productLoreHints ? `Additional hints from the orchestrator (the booted context agent (you)'s lore is the primary source — these are supplementary):\n${productLoreHints}\n\n` : ''}Tasks:

1. **Hunt bugs.** Trace all execution paths through this unit and adjacent components. Report any suspected fault — wrong logic, missing validation, off-by-one, race, dropped error, mishandled edge case. Use the booted context agent (you) to check whether upstream callers already handle the case (a bug is less interesting if it cannot be triggered in practice).

2. **Author comprehensive test scenarios.** Cover not only line + branch coverage but ALSO:
   - product-level edge cases that would change user-visible behavior
   - technical-level edge cases that would cause a fault, integration mismatch, or contract violation
   - boundary conditions, empty/null inputs, malformed inputs, unicode/locale quirks where relevant
   - patterns the booted context agent (you)'s lore flags as historically problematic

Hard rules:
- Every scenario's \`expected\` MUST cite an \`intentSource\` (docstring, type contract, RFC, product-lore topic from the booted context agent (you), etc.). "The current code returns X" is NOT an intent source.
- Every bug's "expected" MUST also cite an intentSource.
- Tag every item with class: product (user-visible behavior) or technical (internal contract).
- Use stable kebab-case ids: scenario ids like "${unit.id}-empty-input", bug ids like "${unit.id}-bug-null-deref".
- Status: "proposed" for scenarios, "unreviewed" for bugs.
- Populate \`loreTopicsConsulted\` with the lore topic filenames you actually used from the booted context agent (you).`,
  { label: `analyze:${unit.id}`, phase: 'Analyze', schema: UNIT_REPORT_SCHEMA }
)))

const cleanReports = unitReports.filter(Boolean)

// ─── Phase 3: Aggregate ──────────────────────────────────────────────────────

phase('Aggregate')

const aggregated = await agent(
  `You are the **file quality analyst** again — now aggregating per-unit reports into a File Report for ${filePath}.

Per-unit results:
${JSON.stringify(cleanReports, null, 2)}

Produce the File Report. \`summary.bugCounts\` should break down by class, severity, and confidence. \`summary.scenarioCounts\` should break down by class and edgeTag. \`perUnit\` carries the unit-level bugs and scenarios verbatim. Add a \`notes\` field with any cross-unit patterns worth flagging.`,
  { label: 'aggregate', phase: 'Aggregate', schema: FILE_REPORT_SCHEMA }
)

// ─── Phase 4: Verify (parallel) — per-bug adversarial + single gap analysis ─

phase('Verify')

const allBugs = aggregated.perUnit.flatMap(u => u.bugs ?? [])
const allScenarios = aggregated.perUnit.flatMap(u => u.scenarios ?? [])

// 4a. Per-bug adversarial verifier — one agent per bug, parallel, attaches context agent.
const bugVerifierThunks = allBugs.map(bug => () => agent(
  `${BOOT_PREAMBLE}

---

You are an **adversarial bug verifier**. Default to **refute**. Only mark a bug "real" if you can independently confirm it from the code + the booted context agent (you)'s repo knowledge.

Bug under review:
${JSON.stringify(bug, null, 2)}

Full file under analysis:
File: ${filePath}
${FILE_BLOCK}

Verify three things:
1. **Reachability** — is the \`triggeringPath\` actually reachable given how this unit is called in the repo? Use the context agent: are there upstream validators, normalizers, or callers that would prevent the input shape this bug requires? If the path is unreachable in practice, the bug is a false-positive *for this codebase* even if technically correct.
2. **Intent-source substance** — does the cited intent source actually say what the bug claims? Cross-check against the docstring, the attached agent's lore, and any external reference cited.
3. **Expected-vs-actual correctness** — is the analyst's "expected" really what the code should do, or is it the analyst's own opinion?

Output a verdict (real / false-positive / inconclusive). Recommend a confidence adjustment (raise / lower / unchanged). Cite the lore topics you consulted.`,
  { label: `verify-bug:${bug.id}`, phase: 'Verify', schema: BUG_VERDICT_SCHEMA }
))

// 4b. Single gap analyzer — runs concurrently with bug verifiers.
const gapAnalyzerThunk = () => {
  if (existingTestFiles.length === 0) {
    log('Gap analysis skipped — no existingTestFiles provided in args')
    return null
  }
  const TEST_BLOCK = existingTestFiles.map(t =>
    `### ${t.path}\n\`\`\`${language}\n${t.contents}\n\`\`\``
  ).join('\n\n')

  return agent(
    `${BOOT_PREAMBLE}

---

You are the **gap analyzer**. Your job is bidirectional-IR gap analysis.

Inputs:

**Proposed scenarios** (from the file analysis):
${JSON.stringify(allScenarios, null, 2)}

**Existing test files** for this unit/file:
${TEST_BLOCK}

Steps:

1. **Reverse-extract** scenarios from each existing test using the same Scenario schema. One existing test may yield multiple scenarios; one scenario may span multiple tests. Use stable ids prefixed \`existing-\`. Cite an intentSource for each (often "the test's own assertion + the unit's docstring"). Use the booted context agent (you)'s lore to identify the *intent* a test embodies, not just its mechanical assertions.

2. **Match** each proposed scenario against the extracted set. Match kind:
   - \`exact\` — same intent + same input shape + same expected
   - \`equivalent\` — same intent, different input/expected representation
   - \`partial\` — overlap but proposed covers more (e.g. proposed checks edge case existing misses)
   Provide a brief rationale per match.

3. **Gap** — for every proposed scenario with no match (and not a partial match that you'd consider sufficient), add to \`gaps\` with a one-line "why" (what aspect is uncovered).

4. **Summary** — real counts only. \`coverageRatio\` formatted "matched/proposed".

Cite the lore topics you consulted in \`loreTopicsConsulted\`.`,
    { label: 'gap-analysis', phase: 'Verify', schema: GAP_ANALYSIS_SCHEMA }
  )
}

const [bugVerdicts, gapAnalysis] = await Promise.all([
  parallel(bugVerifierThunks),
  gapAnalyzerThunk(),
])

const cleanBugVerdicts = bugVerdicts.filter(Boolean)

// ─── Phase 5: Multi-lens review ──────────────────────────────────────────────

phase('Review')

const REPORT_BLOCK = JSON.stringify(aggregated, null, 2)
const VERDICTS_BLOCK = JSON.stringify(cleanBugVerdicts, null, 2)
const GAP_BLOCK = gapAnalysis ? JSON.stringify(gapAnalysis, null, 2) : '(gap analysis was skipped — no existing tests provided)'

const LENSES = [
  {
    key: 'intent-vs-observed',
    prompt: `Lens: **intent-vs-observed**. For every scenario, is \`expected\` derived from intent (per intentSource) or merely observed behavior of the current code? Flag change-detector scenarios.`,
  },
  {
    key: 'completeness',
    prompt: `Lens: **completeness**. Are there obvious branches, edges, error paths, or boundary conditions in the file NOT covered by any proposed scenario? Are there bugs the analyst should have caught but didn't? Reference specific code lines.`,
  },
  {
    key: 'soundness',
    prompt: `Lens: **soundness**. Re-check the bug verdicts and gap analysis output. Are any verdicts wrong (false-positive marked as real, or vice versa)? Does the gap analysis miss real overlaps or fabricate overlaps that aren't there?`,
  },
]

const reviews = await parallel(LENSES.map(l => () => agent(
  `${l.prompt}

File: ${filePath}
${FILE_BLOCK}

File Report:
${REPORT_BLOCK}

Bug verdicts:
${VERDICTS_BLOCK}

Gap analysis:
${GAP_BLOCK}

Return findings keyed by target id (unitId / scenarioId / bugId / "gap-analysis"). Severities: nit / minor / major.`,
  { label: `review:${l.key}`, phase: 'Review', schema: REVIEW_SCHEMA }
)))

return {
  filePath,
  units: units.length,
  report: aggregated,
  bugVerdicts: cleanBugVerdicts,
  gapAnalysis,
  reviews: reviews.filter(Boolean),
}
