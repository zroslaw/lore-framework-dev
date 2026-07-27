    if not matches:
        res.fail("agent '%s' not found in %s" % (args.agent, workspace))
        res.data["available_agents"] = [
            {"name": a["name"], "repo": a["repo"], "description": a["description"]}
            for a in agents
        ]
        return None
    if len(matches) > 1:
        res.warn("agent name '%s' is ambiguous across %d repos; using %s"
                 % (args.agent, len(matches), matches[0]["repo"]))
    return matches[0]


def cmd_preflight(args, res):
    """The boot/attach/consult/merge preflight. This function's steps ARE the
    normative procedure (docs/conventions.md § Script Fallback Contract) — if
    this script cannot run, read the six steps below (and the referenced
    helper functions for their own exact commands) and execute them by hand.

    Step 1: resolve <framework-root> (this script's grandparent dir, or
    --framework-root) and read its VERSION file. Missing/unreadable VERSION is
    a warning, not a failure — the version check below just becomes
    inconclusive.

    Step 2: resolve the target agent. If --agent-dir was given, use it
    directly: require a role.md there, and derive the repo root by walking up
    two directories and checking for lore-repo.md (warn, don't fail, if that
    check comes up empty — repo-scoped steps 4-5 below are skipped for a
    repo-less agent). Otherwise, discover every repo under <workspace> and
    match --agent by name; no match is a failure (report available_agents);
    more than one match is a warning (use the first, arbitrarily). See
    _resolve_agent below for the exact logic.

    Step 3: record the agent's role.md and lore-context.md paths as
    `read_next`. Reading and interpreting those files is the caller's job —
    their content is judgment material, not something this script parses.

    Step 4: if the agent sits under a real lore repo, auto-pull it (TTL-cached
    — see pull_repo below for the exact `git pull --ff-only` invocation, the
    fast-fail env vars, and the `.git/lr-last-pull` TTL stamp file), then
    compare the repo's lore-repo.md version stamp against the framework
    VERSION read in Step 1 (see compare_versions below for the exact match/
    skew rules). A failed pull is a warning ("continue in degraded mode"), not
    a stopping condition. Version skew other than an exact match is also a
    warning pointing at docs/version-check.md.

    Step 5: otherwise (no enclosing repo — the warning from Step 2), skip both
    of those: report pull as "skipped" and version as "unknown", and run no
    git subprocess at all.

    Step 6: detect an Agent-Teams teammate spawn (see detect_teammate below for
    the exact `ps -o args= -p <ppid>` walk and the `--agent-id` flag-boundary
    match), unless --no-teammate-check suppressed it.
    """
    workspace = os.path.abspath(args.workspace)
    root = resolve_framework_root(args.framework_root)
    fw_version = framework_version(root)
    if fw_version is None:
        res.warn("no readable VERSION at %s — version check will be inconclusive" % root)

    res.data["framework_root"] = root
    res.data["workspace"] = workspace

    agent = _resolve_agent(args, res, workspace)
    if agent is None:
        return res

    role_file = os.path.join(agent["dir"], "role.md")
    lore_context_file = os.path.join(agent["dir"], "lore-context.md")
    if not agent["has_lore_context"]:
        res.warn("no lore-context.md at %s — agent has no compacted knowledge yet"
                 % agent["dir"])

    res.data["agent"] = {
        "name": agent["name"],
        "dir": agent["dir"],
        "repo": agent["repo"],
        "description": agent["description"],
        "role_file": role_file,
        "lore_context_file": lore_context_file if agent["has_lore_context"] else None,
    }
    # The files the caller must read into context next. Reading them is the
    # caller's job: their content is judgment material, not script output.
    res.data["read_next"] = [p for p in (role_file, lore_context_file if
                                         agent["has_lore_context"] else None) if p]

    if agent["repo"]:
        # Step 4 (repo branch): TTL-cached pull, then version compare.
        res.data["pull"] = pull_repo(
            agent["repo"], ttl=args.ttl, fresh=args.fresh, do_pull=not args.no_pull)
        if res.data["pull"]["status"] == "failed":
            res.warn("auto-pull failed for %s: %s — continue in degraded mode"
                     % (agent["repo"], res.data["pull"]["detail"]))
        repo_version = parse_frontmatter(
            read_text(os.path.join(agent["repo"], "lore-repo.md"))).get("version")
        res.data["version"] = compare_versions(repo_version, fw_version)
        verdict = res.data["version"]["verdict"]
        if verdict in ("repo-behind", "repo-ahead", "differs"):
            res.warn("version skew: repo=%s framework=%s (%s) — see version-check.md"
                     % (repo_version, fw_version, verdict))
        elif verdict == "unknown":
