# Recovery evidence and proof limits

This is the public evidence ledger for the [specification](spec.md), [plan](plan.md) and [work items](work-items.md). It separates source contracts, prototype reports, this fork's offline checks and evidence still required. A source example is not this fork's recovery proof. Live documentation links are mutable; repository sources below are pinned.

## Implementation baseline

The original Claude integration is at [`69f5497d3d3dec7ad3269c72ff266c2931c9f379`](https://github.com/osamastro7-droid/ai-integrations/tree/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk). The development fork adds a [dependency lock repair](https://github.com/mortdiggiddy/ai-integrations/commit/d70ce0b13a3b3eca07707ccc88c8a9494bd58032) and [offline policy and harness implementation](https://github.com/mortdiggiddy/ai-integrations/commit/99fb461a074debfcaff6308cb0a3454b93991ed2). The [README and responsibility diagram](https://github.com/mortdiggiddy/ai-integrations/commit/2acc081998407f9c88fdba349103f5392dab2d73) clarify the target but add no runtime proof.

The policy table and option checks, complete paused request identity binding, refusal when an executor is missing and offline harness controls are implemented. Validated skill loading, the effect executor and signed human decision handling are not implemented. The legacy default is retained when policy mode is unset. See the [plugin README](../../README.md) for the implemented API rather than interpreting proposed interfaces as released behavior.

Relevant committed tests include [policy tests](https://github.com/mortdiggiddy/ai-integrations/blob/99fb461a074debfcaff6308cb0a3454b93991ed2/python/claude_agent_sdk/tests/test_tool_policy.py) and [offline harness tests](https://github.com/mortdiggiddy/ai-integrations/blob/99fb461a074debfcaff6308cb0a3454b93991ed2/python/claude_agent_sdk/tests/test_offline_harness.py). They cover exact names, rejected permission extras, request identity mismatch, denial after stop, Skill denial without a validator, checkpoint comparison, paid execution refusal, cancellation and report redaction. They do not establish actual model interception or safe Bash recovery.

Recorded local verification at the implementation checkpoint passed repository conventions, 101 tooling tests, locked dependency installation, lint and the complete default integration suite. The dependency repair checkpoint passed 104 integration tests. These are historical local results on Linux with Python 3.13.15, SDK 0.2.154 and engine 2.1.274, not a fresh run for this documentation package. They do not establish the complete supported platform matrix, distribution checks, hosted CI, real model behavior or candidate adoption. No hosted check ran for the feature branch tip; absence of a check is not a pass.

## Source contracts and candidate evidence

| Evidence | Source and revision | What it supports | What it does not prove |
|---|---|---|---|
| Native skills | [SDK skills](https://code.claude.com/docs/en/agent-sdk/skills) | Claude owns filesystem skill discovery and invocation. | Startup inventory is not proof that actual model or command invocation stays within a validated package. |
| Session persistence | [SDK sessions](https://code.claude.com/docs/en/agent-sdk/sessions) | Conversation checkpoints can be stored or transferred separately from execution. | Session history does not restore the workspace, protected claims or exclusive ownership. No new database is mandated. |
| Deferred calls | [Claude hook protocol](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later) | A resumed call is checked again and may be deferred again. | Synthetic host result delivery is not established by the documented allow on resume path. Batch behavior and permission precedence still require proof. |
| Hybrid recovery | [Prototype README](https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/README.md) | Reports a long running CLI, recovery of original pending main requests, recorded outcomes and a bounded Read/Edit workspace replay experiment. | Reported prototype tests were not rerun for this publication. A deterministic local Messages API is not real model evidence. One file is not general workspace or Bash durability. |
| Experimental SDK recovery | [Recovery implementation](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/src/claude_agent_sdk/_internal/main_agent_recovery.py) | Recovery before replacement CLI startup, conditional transcript append and readback; host responsibility for exclusive ownership. | Released SDK support, pending child agent recovery, graceful suspension or orphan cleanup after machine loss. |
| Mods | [Official announcement](https://claude.dev/blog/getting-started-with-claude-code-mods/) and [pinned declarations](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/types/claude-code.d.ts) | Candidate tool interception and result replacement; local persistent store distinct from reload state. Failed, over budget or malformed hooks can be skipped. | Actual loading through this Python SDK lane, complete coverage, distributed ownership or an atomic transaction with external effects. An independent preventive control is still required. |
| Effect completion gap | [Temporal Activity idempotency](https://docs.temporal.io/activity-definition#idempotency) | Effects and recorded Activity completion are separate failure boundaries. | A recovered session or accepted approval cannot establish that an uncertain Bash effect is safe to repeat. |
| Reusable Workflow integration | [Workflow friendly libraries](https://docs.temporal.io/develop/plugins-guide#workflow-friendly-libraries) | Reusable orchestration can remain in deterministic Workflow code while filesystem and network operations run outside it. | This fork's registration, security and policy implementation or compatibility with every application Workflow. |
| Control state precedent | [Safe handlers example](https://github.com/temporalio/samples-python/blob/811062812152519af5bc078375aaf061c9bda6ae/message_passing/safe_message_handlers/workflow.py) and [history replay example](https://github.com/temporalio/samples-python/blob/811062812152519af5bc078375aaf061c9bda6ae/replay/replayer.py) | Control state, handler coordination and replay test patterns. | Claude, Mods, filesystem recovery or this project's signed human decisions. |

The candidate source review is dated 2026-10-01. Its recommendation is to investigate hybrid CLI recovery and experimental main agent recovery first, compare against the implemented defer path and evaluate Mods as candidate interception. It is not an adoption decision. A publication freshness check could not retrieve the three pinned candidate pages through the browser; the ledger retains the previously inspected immutable revisions and makes no fresh remote verification claim.

## Required recovery evidence

For each candidate, record exact SDK and CLI versions, dependency provenance, loading route, permission configuration and source revisions. Classify each scenario as observed success, failed requirement, unsupported or unexecuted. Never count an unexecuted case as passing.

- Actual SDK skill and Mods invocation, including command dispatch and hidden or bundled skills; the discovered skill list alone is insufficient.
- Original request ID, exact name and canonical inputs; result and error metadata survive supported recovery without rerunning recorded effects.
- Disabled, missing, throwing, over budget and malformed hooks cannot cause unrecorded effects. Record bypass coverage and independent prevention or reject the candidate.
- A pending decision survives loss of the original Worker and is accepted once. Competing owners and stale CLI processes cannot continue the same session.
- Replacement Workers restore the session, required files, validated package, manifest and protected claims. Missing or inconsistent state blocks continuation.
- Inject failure before execution, after mutation or external effect, and before outcome publication. Compare filesystem hashes and the published result.
- Ambiguous Bash parks with no second spawn and no next model turn. A candidate that cannot enforce this does not meet the offered scope.

Replacement Worker and pending decision checks require a Temporal test rig and recorded history. Isolated defer seam checks may omit a Temporal server. Fake model compatibility tests precede any separately budgeted real model run. Real model proof, supported platform and dependency lanes, recorded history replay, full workspace restoration and the later harness adapter remain outstanding.

## Documentation verification boundary

A limited independent review found the project goal, research priority and test rig distinction consistent across the source design package and pinned README. It did not establish a full design verdict, SDK compatibility, recovery viability or runtime acceptance. The public adaptation must be checked for preserved requirements, resolvable links, source boundaries and private information before it is committed. Documentation checks cannot retire runtime assumptions.

## Bounded comparison on the existing dependency lane (2026-10-01)

These dispositions describe the initial batch. The [native file follow up](#bounded-native-file-replay-comparison-2026-10-01) adds later bounded evidence on the same dependency lane.

The comparison began from clean branch `design-base` at `c0d50319fc5835f324ef2a34be2fe7a26ff4eda1`. It investigated the pinned hybrid and experimental main recovery sources first, then exercised the implemented defer baseline and Mods loading. The installed environment was Linux, Python 3.13.15, `claude-agent-sdk` 0.2.154, bundled CLI `2.1.274 (Claude Code)`, `temporalio` 1.33.0 and plugin 0.0.0. No experimental fork was installed and no dependency version or lockfile changed. All model requests used a local scripted Messages API with isolated configuration and synthetic credentials. CLI list price estimates for those scripted responses are not paid model charges.

The scripts under [experiments](experiments/) reproduce the compatibility, defer and process observations. Their generated records distinguish observed success, failed requirement, unsupported invocation and unexecuted scenario. A successful experiment process does not mean every comparison requirement passed: the malformed identity and competing owner probes intentionally record failures of the offered recovery contract. These scripts exercise the installed package rather than replace it with candidate code.

### Reproduction and artifacts

Run from this repository's root using the existing noneditable environment. `--no-sync` prevents dependency installation. The experiment scripts require the tested Python 3.13 lane and write their transcripts, requests, reports and local fixtures only beneath the supplied scratch directory. Choose a fresh directory for each run. The replacement rig uses the cached binary whose printed version is `temporal version 1.8.3-server-1.32.0-162.0 (Server 1.32.0-162.0, UI 2.53.1)`; it starts a local development namespace and default server configuration with no custom dynamic configuration. Shared paths in this single host experiment are not production storage guarantees.

```bash
make -C python/claude_agent_sdk test PYTEST='uv run --no-sync pytest -n 0' PYTEST_ARGS='tests/test_tool_policy.py tests/test_offline_harness.py tests/test_engine.py --junit-xml=/tmp/recovery-comparison-existing.xml'
make -C python/claude_agent_sdk test PYTEST='uv run --no-sync pytest -n 0' PYTEST_ARGS='tests/test_installed_matches_source.py --junit-xml=/tmp/recovery-comparison-provenance.xml'
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/compatibility.py
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/baseline.py --root /tmp/recovery-comparison-reuse --case reuse
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/baseline.py --root /tmp/recovery-comparison-replacement --case replacement --server /tmp/temporal-v1.8.3-server-1.32.0-162.0
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/baseline.py --root /tmp/recovery-comparison-orphan --case orphan --server /tmp/temporal-v1.8.3-server-1.32.0-162.0
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/mods.py --root /tmp/recovery-comparison-mods
```

Fresh existing-suite results were 204 passed with 30 no-credentials warnings, followed by one passing installed/source provenance test. Compatibility construction executed no CLI or model. Selected experiment outputs are retained under [results](experiments/results/); reproduction also emits raw local model requests and session transcripts beneath its scratch root. The legacy fake refund data is synthetic test data already used by this repository. Machine roots and host labels in archived records are replaced with `<scratch>`, `<repo>` or `experiment-host`; request IDs, canonical inputs, outcome payloads and event ordering are preserved.

### Findings and dispositions

| Case | Implemented defer baseline | Hybrid and experimental main recovery | Mods interception |
|---|---|---|---|
| Actual dependency compatibility | Observed: installed SDK and real bundled CLI run against the fake API. | Experimental main recovery unsupported in this wheel: constructing `ClaudeAgentOptions(recover_pending_tool=...)` raises `TypeError`; both recovery options and the main recovery module are absent. The narrower native replay prototype reports published SDK compatibility and remains a separate unexecuted candidate. | Observed unsupported interception: SDK forwards `--plugin-dir`, CLI lists the plugin, but the unique `tool.call` deny marker is absent and the correlated harmless native Read result reaches the fake model. The same CLI validates the module fixture; failure is activation/interception in this invocation, not proof that its parser lacks module syntax. |
| Exact request and recorded success/error reuse | Observed in the legacy custom MCP lane: original ID, exact name and inputs retain their stored payload and `is_error`; in-engine stub execution count stays zero. No effect executor is supplied by this probe. | Source binds original session/ID/name/input/transcript UUID and conditionally appends/readbacks the outcome. Runtime result reuse is unexecuted without the experimental dependency. | Native Read request/result ID correlation observed; replacement result/error and crash recovery are unexecuted because interception did not load. |
| Changed identity | Failed requirement in legacy custom MCP lane: wrong injected ID reaches one further fake model request with an internal missing-result placeholder before the runner returns a pause contract error. Existing policy tests separately exercise name/input/marker guards; they are not this real engine mismatch proof. | Exact identity mismatch refusal supported by pinned source; runtime unexecuted. | Runtime identity mismatch unexecuted. |
| Missing checkpoint or persisted conversation | Observed refusal: missing checkpoint and empty replacement store each raise an explicit engine error and make no continuation model request. This does not prove missing package, manifest or claims refusal. | Source refuses missing transcript; runtime unexecuted. | Unexecuted. |
| Pending approval after Worker loss | Observed on a real Temporal rig: killed first Worker and replacement with empty engine configuration report identical pending ID/name/input, zero model requests during replacement and one refund execution after approval. Uses the existing legacy custom MCP example and a shared local session folder. Signed gateway, duplicate decision acceptance and native skill approvals remain unexecuted. | Prototype reports original pending main recovery. Not rerun with the experimental fork. | Unexecuted. |
| Exclusive ownership | Failed requirement: two concurrent resumes of the same accepted checkpoint both continue and receive the recorded result. No host lease is supplied by the runner. | Pinned SDK explicitly assigns exclusive session ownership through CLI teardown to the host. Runtime contention unexecuted. | Local store supplies no distributed ownership proof; runtime contention unexecuted. |
| Orphan process after Worker loss | Failed requirement on a real Temporal rig: killing the Worker while its first local model request is blocked leaves its CLI descendant alive with the same process start identity. No effect executes. The experiment terminates that verified owned descendant and confirms no active owned process remains; it does not start a replacement while an orphan exists. This cleanup belongs to the experiment, not the implemented integration. | Host supervision remains required by source and unexecuted for the candidate. | Unexecuted. |
| Native file mutation before outcome publication | Unexecuted: general native effect executor does not exist. The custom MCP refund rig does not establish native file semantics. | Pinned native replay fixture covers one regular file and includes this fault seam. Exact fixture and its Temporal import closure were not executed in this batch. Its published SDK lane must not be rejected merely because experimental main recovery is absent. | Unexecuted. |
| Missing/disabled/throwing/over budget/malformed hook; permission order and child/plugin routes | Existing policy unit tests passed; actual engine prevention and alternate invocation coverage remain unexecuted in this comparison. | Unexecuted; pending Agent/Task recovery explicitly excluded by source. | All five controls and alternate routes unexecuted after the loading rejection. A successful plugin listing is not interception or a preventive backstop. |
| Ambiguous Bash after effect/before completion | Unsupported by the currently implemented effect path; no Bash effect or uncertainty continuation was launched. Claimed executor and immediate park proof remain open. | Unexecuted and outside the bounded file example. No snapshot or recovered callback can establish an uncertain Bash outcome. | Unexecuted. Local hook storage is not an atomic effect/outcome transaction. |

### Recovery state limits

Final lead reruns used the frozen scripts for result reuse, pending approval replacement, orphan detection and Mods interception. All experiment assertions passed while preserving the failed requirement dispositions above. The orphan fault produces an expected local fake API disconnect traceback after the owned client is terminated. The replacement run reports a slow Workflow query during recovery; its captured history and final outcome assertions succeed. Selected records include [reuse results](experiments/results/reuse.json), [pending approval replacement](experiments/results/replacement.json), [replacement history](experiments/results/replacement-history.json), [orphan observation and cleanup](experiments/results/orphan.json), [orphan history](experiments/results/orphan-history.json), [SDK compatibility](experiments/results/compatibility.json) and [Mods results](experiments/results/mods.json).

Conversation recovery is supported by the bounded legacy defer observations. Workspace and protected claims recovery remain unproved: the replacement test preserves a shared local folder, does not remove the original disk, and does not validate a package, manifest, claims or production volume. Approval and outcome recovery is demonstrated only for the existing legacy custom MCP example. These state classes have different proof limits even when the test keeps them on one host.

The hybrid source offers two routes. Live pending main recovery requires the experimental options callback, not a client `recover` method. The native Read/Edit replay fixture uses the released SDK through private session APIs, a local cached response and a one file publication ledger. Its activities require a Temporal context and its after mutation fault requires the complete fixture and rig; a direct class call would not prove Worker replacement. Neither route supplies the complete native skill, workspace/claims, single owner, orphan containment and ambiguous Bash contract on this tested lane.

Fresh pinned source reads checked the [native replay boundary](https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/tests/hybrid/native_replay.py#L230-L351), [hybrid recovery callback](https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/tests/hybrid/engine.py#L117-L176), [experimental transcript recovery](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/src/claude_agent_sdk/_internal/main_agent_recovery.py#L150-L243) and [SDK host ownership contract](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/src/claude_agent_sdk/types.py#L1672-L1688). These reads supersede the earlier publication's retrieval limitation for those sources, not its runtime limits.

Temporal Docs retrieval reconfirmed the [effect before Activity completion gap](https://docs.temporal.io/activity-definition#idempotency): a recorded approval does not establish effect completion. Atlas discovery returned supporting integration descriptions but no direct candidate recovery contract, so its results do not retire these assumptions. No internal Atlas source material is reproduced here.

### Dependency and fixture proposals

An experimental main recovery run would require a separate disposable environment and a noneditable wheel built from SDK revision `3ac4b25733d1302c89d0dadd13cab268e64d1213` (declared version 0.2.162). Its runtime requirements are already present in the tested environment: anyio 4.15.1, sniffio 1.3.1, MCP 2.2.0 and jsonschema 4.26.0. Its unpinned `hatchling` build dependency is absent. A concrete build dependency version/hash and any transitive additions must be proposed before installing. Retain the existing CLI via explicit `cli_path` for the first comparison; changing CLI versions is a separate dependency proposal. Do not run the prototype's `make sync` or auto provisioning fixtures unchanged: they install the fork or download a CLI.

A separate released SDK experiment could extract the pinned native replay fixture and its exact test import closure into a disposable directory without replacing installed SDK/plugin modules. That experiment requires a Temporal rig, captured Workflow history, an explicit source manifest and safe process ownership for fault injection. It was not executed here. Mods needs a verified function hook activation route and a separately selected compatible CLI; the earlier announcement review reported a 2.1.287 minimum, but the announcement could not be retrieved freshly in this batch. The pinned declaration header identifies a different generated build and is not evidence of activated interception in the installed CLI. No enabling flag is inferred from a successful parser check. No minimum version, cooldown exception or architecture is changed by these proposals.

### Recommendation and open proof

Retain the implemented defer path as the comparison baseline while keeping executor entry blocked. Reject Mods interception for the actual tested SDK/CLI invocation. Defer adoption of experimental main recovery until its isolated dependency proposal and host ownership/supervision proofs are resolved. Keep the narrower native file replay route as an unexecuted candidate, with its file and publication limits explicit. This is a recommendation to [integration adoption](work-items.md#integration-adoption), not adoption or a production readiness verdict.

A-57 is unsupported for the tested Mods invocation; A-58 remains open because exact accepted request recovery with exclusive ownership and orphan prevention is not established; A-59 remains open because general native file and protected state recovery was not executed. The malformed ID, competing resume and orphan findings require resolution or an explicitly excluded invocation before claiming the full recovery contract. Paid model acceptance, validated native skill execution, signed decisions, complete hook prevention, general workspace recovery and ambiguous Bash park behavior remain outstanding.

## Bounded native file replay comparison (2026-10-01)

This follow up tests the released SDK native Read/Edit replay route at hybrid revision `2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f`. The installed SDK remains 0.2.154, Claude CLI remains 2.1.274, Temporal SDK remains 1.33.0 and plugin remains 0.0.0 on Python 3.13.15. No experimental SDK was built or installed. All model requests use a local fake Messages API and isolated configuration with synthetic credentials; paid calls remain disabled.

The [source manifest](experiments/results/native-source-manifest.json) records 28 files verified against pinned Git blob identities and SHA256 hashes. The custom Worker uses only the 14 file runtime import closure; the remaining files are inspection material. Source pytest configuration and its provisioning fixtures are not executed. The [fetch helper](experiments/fetch_native_source.py) reproduces the extraction and refuses a hash mismatch before publishing the source directory. A fresh lead extraction verified all 28 files, followed by an independent lead rerun of all three replacement cases.

The [rig](experiments/native_replay.py) calls the unchanged pinned `ReplayActivities`, `ReplayStore` and `NativeReplayWorkflow` with the installed packages. Its custom Worker entry point avoids the source Worker's unrelated experimental branches. The invocation offers and allows only Read/Edit, uses `acceptEdits`, empty setting sources, no MCP servers, strict MCP configuration and eager session mirroring. These candidate fixture settings do not prove the production policy's default permission boundary. The [invocation record](experiments/results/native/invocation.json) pins the actual CLI and server binary hashes; the server uses the same cached local development binary, default namespace, in-memory persistence and no custom dynamic configuration as the preceding batch.

### Reproduction

Run from the repository root with a fresh source directory and output directory. Source retrieval requires read access to GitHub through the installed `gh` command. It installs no package and executes no fetched fixture. The second command needs the existing environment and cached Temporal binary; it supplies the original installed CLI explicitly and removes inherited hybrid CLI overrides.

```bash
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/fetch_native_source.py --root /tmp/recovery-native-source
python/claude_agent_sdk/.venv/bin/python python/claude_agent_sdk/docs/skill-recovery/experiments/native_replay.py --source-root /tmp/recovery-native-source --repo python/claude_agent_sdk --root /tmp/recovery-native-run --server /tmp/temporal-v1.8.3-server-1.32.0-162.0
```

One initial setup run stopped before replacement because the CLI inserted the omitted Edit default `replace_all: false`, making the synthetic request assertion differ from the accepted transcript. The corrected fixture emits that argument explicitly and keeps exact ID/name/input equality. This is a recorded harness input normalization issue, not a candidate rejection. Its [diagnostic](experiments/results/native/normalization-diagnostic.json) confirms owned process cleanup. A corrected subagent run and the final lead run both passed all three cases. An independent reviewer verified the exact execution mirror selection, request identity, original and published native results, file hashes and cleanup records.

### Results

| Fault boundary | Native Edit invocations | Committed Edit outcomes | Recovery result |
|---|---:|---:|---|
| [After publication, before Activity completion](experiments/results/native/committed-edit/report.json) | 1 | 1 | Replacement reuses the original success result and native metadata. The final file contains `AFTER\n`. |
| [After mutation, before publication](experiments/results/native/unpublished-edit/report.json) | 2 | 1 | At the fault, the physical file contains `AFTER\n`, the retained snapshot contains `BEFORE\n`, and no Edit outcome is published. Replacement restores the snapshot and executes the same accepted Edit again. The final file contains `AFTER\n`. |
| [Published native validation error, before Activity completion](experiments/results/native/native-error/report.json) | 1 | 1 error | Replacement reuses the original native error and metadata with `is_error` preserved. The invalid Edit leaves the file at `BEFORE\n`. |

Every case preserves the original Edit decision, including ID, exact name, canonical arguments, session, round, position, batch, source digest and transcript UUID. Original and published Edit result blocks and native `toolUseResult` metadata match on these runs. Full transcript carriers differ: committed results reattach their parent UUID, while the unpublished case creates a new execution carrier. Read executes once and its recorded result reaches the final conversation; complete original/published Read native metadata parity is not separately asserted.

Each case has two upstream fake decision requests before the fault and one continuation after recovery. The local cached execution endpoint receives two requests in the committed/error cases and three in the rollback case; it replays the accepted assistant block rather than asking the upstream model to regenerate an effect request. Each history schedules exactly one Read and one Edit Activity; Activity retries account for the second physical Edit. All three exported histories pass Workflow replay. The final file mode is `0640`; SHA256 is `f72c713b7b432dd18949ca10f1be6dbcf493479945653609d1c715b2d8d74356` for `AFTER\n` and `be9351741a8155d01fd028d158546f1005e73ceeb0bb2d093335feac4144e450` for `BEFORE\n`.

The [native results directory](experiments/results/native/) retains per-case fault snapshots, accepted calls, original/published native outcomes, upstream model requests, histories and reports. Machine paths and host names are normalized in archived records, including encoded history payloads and ephemeral device identifiers; result carrier and receipt hashes describe the original runtime bytes before normalization. File, source and binary hashes remain directly verifiable.

### Proof limits and recommendation

The rig kills the first Worker, verifies process start identities and accounts for its descendants before replacement. Every cleanup record has no active owned process left. Sequential ownership and that cleanup are supplied by the experiment, not established production lease or orphan controls. The rig deletes the working file directory, first Worker configuration, local attempt mirrors and response cache directories. It preserves the SQLite conversation, accepted receipt, outcome and single file snapshot store on the same host. This demonstrates reconstruction from that retained projection; it does not demonstrate original disk removal, a second host, package/manifest restoration, protected claims, volume conformance or loss of the retained store.

Missing/corrupt snapshots, changed receipts and stale/concurrent owners were not exercised in this batch. Signed decisions, native skill loading, permission bypass routes, child/plugin/background recovery, graceful cancellation and ambiguous Bash remain unproved. Only regular-file Read/Edit is offered. The rollback path can repeat a physical Edit; it does not satisfy the single spawn Bash uncertainty contract. Ambiguous Bash remains outside the offered candidate scope and must park without another spawn or model continuation.

The narrower native replay route is now a supported candidate for these bounded fake model cases on the existing dependency lane, replacing its prior unexecuted disposition for those cases only. It is not adopted. Retain defer as the implementation baseline with executor entry blocked; carry native replay forward for comparison with experimental main recovery. A-57 remains unsupported for the tested Mods invocation, A-58 remains open for complete ownership and process recovery, and A-59 remains open for general filesystem and protected state recovery. The dependency proposal below defines the next unexecuted experiment prerequisite.

### Experimental main recovery dependency proposal

Status: proposed, not installed or built.

The installed SDK is 0.2.154 and does not expose `ClaudeAgentOptions.recover_pending_tool` or `parallel_tool_recovery`. The experimental source at revision `3ac4b25733d1302c89d0dadd13cab268e64d1213` declares SDK version 0.2.162. This proposal changes only a disposable environment for fake model recovery experiments. It does not change repository manifests, lockfiles, the installed baseline environment, or the selected CLI.

#### Source and CLI identities

| Input | Identity |
|---|---|
| SDK source | `https://codeload.github.com/brianstrauch/claude-agent-sdk-python/tar.gz/3ac4b25733d1302c89d0dadd13cab268e64d1213` |
| Source archive SHA256 | `364ec9f343f793dd5ce9c8aa4bc685101286c732b47a19d90171b15e1db6a022` |
| Existing CLI | `2.1.274 (Claude Code)` |
| Existing CLI SHA256 | `15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07` |

The source archive was streamed to a hash command for inspection. It was not saved, extracted, built or installed. The existing CLI remains selected by explicit `cli_path`; compatibility with the experimental SDK remains a runtime experiment, not a conclusion from the SDK version.

#### New build dependencies

| Package | Pin | Wheel SHA256 | Registry upload date |
|---|---|---|---|
| hatchling | 1.27.0 | `d3a2f3567c4f926ea39849cdf924c7e99e6686c9c8e288ae1037c8fa2a5d937b` | 2024-12-15 |
| trove-classifiers | 2026.6.1.19 | `ab4c4ec93cc4a4e7815fa759906e05e6bb3f2fbd92ea0f897288c6a43efd15b3` | 2026-06-01 |

Metadata was read from [Hatchling registry metadata](https://pypi.org/pypi/hatchling/1.27.0/json) and [classifier registry metadata](https://pypi.org/pypi/trove-classifiers/2026.6.1.19/json). Both wheels are not yanked and exceed the existing two week cooldown. Classifiers have no declared dependencies. Hatchling requires `packaging>=24.2`, `pathspec>=0.10.1`, `pluggy>=1.0.0` and `trove-classifiers`; its `tomli` requirement applies only below Python 3.11.

Already installed build dependencies satisfy those metadata bounds: packaging 26.3, pathspec 1.1.1 and pluggy 1.6.0. Runtime dependencies also satisfy the experimental SDK metadata: anyio 4.15.1, sniffio 1.3.1, MCP 2.2.0 and jsonschema 4.26.0. Temporal remains 1.33.0 and Python remains 3.13.15. Metadata compatibility does not prove build or runtime compatibility.

#### Build boundary

The pinned [pyproject](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/pyproject.toml) names `hatchling.build` and declares no custom Hatch build hook. Its wheel target includes the SDK package. The separate [wheel helper](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/scripts/build_wheel.py#L640-L647) downloads a CLI unless `--skip-download` is supplied, and calls a build frontend that can provision build isolation dependencies. That helper is outside this proposal.

Use `hatchling.build.build_wheel` directly from the approved isolated environment, with the source directory as the subprocess working directory. Keep the source `_bundled` directory free of CLI binaries and use the existing external CLI through `cli_path`. This needs no `build`, `wheel`, `twine`, `zopfli`, CLI download, platform retagging or source version edit.

#### Proposed build procedure (unexecuted)

1. Copy the existing noneditable environment into a disposable prefix using `cp -a <baseline-venv> <isolated-venv>`. Invoke its Python directly and pass that exact executable to every `uv pip --python` command. Do not activate the copied environment or invoke copied console scripts, whose shebangs can still point at the original prefix. Confirm the copied interpreter's `sys.prefix` and installed distributions resolve under the disposable prefix before modifying it. Capture every baseline distribution and version before and after; only the SDK replacement and the two named build additions may differ. The baseline directory is never an installation target.
2. Download only the two listed wheels and the immutable SDK archive. Verify the stated SHA256 hashes before use. Install the two build wheels into the disposable environment using `uv pip install --python <isolated-python> --no-index --find-links <verified-wheel-directory> --no-deps --require-hashes -r <approved-build-requirements>`; the requirement file contains only these two pins and hashes. Give uv a scratch cache directory. No resolver updates are allowed.
3. Extract the verified SDK archive into the disposable directory. Invoke `<isolated-python> -c 'from hatchling.build import build_wheel; print(build_wheel("<wheel-output>"))'` with the source directory supplied as `cwd`. This direct backend build uses the already approved dependencies and performs no frontend build isolation.
4. Record the generated wheel SHA256 and metadata, then install only that local wheel into the disposable environment with `uv pip install --python <isolated-python> --no-index --no-deps <wheel>`. Verify module provenance, both recovery options, unchanged existing dependency versions, and the existing CLI hash/version before any recovery test.
5. Run the separately reviewed fake model recovery cases against the Temporal rig with credentials absent. Capture exact request/result identity, approval reuse, session ownership, process cleanup and replacement histories. Declared child recovery exclusions remain excluded. Any missing dependency, build incompatibility or CLI incompatibility stops the batch and requires a revised proposal before an addition or version change.

No step grants adoption, executor implementation, a repository commit, push, paid model call or external contact. Only the disposable SDK version changes under this proposal.
