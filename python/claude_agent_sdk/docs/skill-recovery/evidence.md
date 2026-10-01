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
