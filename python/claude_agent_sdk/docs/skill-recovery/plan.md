# Recoverable skill execution plan

This is the implementation plan for the [specification](spec.md). [Work items](work-items.md) own completion status and runnable acceptance criteria. [Evidence](evidence.md) separates source observations, executed tests and unresolved proof. These files are the canonical design package; documentation describes a target unless evidence explicitly establishes current behavior.

## Current checkpoint

The historical plugin baseline is `69f5497d3d3dec7ad3269c72ff266c2931c9f379`. Dependency repair `d70ce0b13a3b3eca07707ccc88c8a9494bd58032` and offline implementation `99fb461a074debfcaff6308cb0a3454b93991ed2` extend that baseline. README revision `2acc081998407f9c88fdba349103f5392dab2d73` records the recoverable skill goal and research direction, not a new runtime recovery proof.

The opt in policy and offline harness are constructed but incomplete. Offline tests do not prove real engine interception, native skill execution, paid budget enforcement, effect recovery or replacement Worker behavior. The package validator, effect executor and signed decision integration remain open. Leaving `tool_policy` unset preserves the existing plugin path.

The bounded existing dependency comparison is [recorded in evidence](evidence.md#bounded-comparison-on-the-existing-dependency-lane-2026-10-01), followed by [native file recovery](evidence.md#bounded-native-file-replay-comparison-2026-10-01) on the unchanged SDK lane. It retains the current integration and leaves adoption and executor entry open. Exact result reuse and a legacy pending approval replacement case succeeded; malformed result identity, concurrent continuation and orphan observations prevent a full recovery claim. General filesystem/claims, signed decisions and ambiguous Bash proof remain outstanding. The [experimental main comparison](evidence.md#bounded-experimental-main-recovery-comparison-2026-10-01) now establishes bounded MCP outcome and pending approval recovery in a disposable SDK installation. It refuses invalid result identity before continuation but still permits simultaneous completed resumes and leaves orphan containment to the host. Retain defer as baseline; no candidate is adopted and general executor entry remains blocked.

The [second bounded host contract batch](evidence.md#bounded-host-contract-comparison-2026-10-01) now records disposable local lease/teardown and controlled orphan containment, eight real native Bash/state refusal parks, and signed approve/reject binding across Worker replacement. Accounting alone permits orphan continuation. The signing rig needs explicit cryptography passthrough and does not prove the production sandbox or gateway contract. Keep the remaining deployment, process, filesystem/claims, permission and signing work open. These adapter measurements do not select an integration or authorize general executor implementation.

## Direction and adoption boundary

Investigate the hybrid long running CLI and experimental main agent SDK recovery first. Compare them with the implemented defer path, and evaluate Mods as candidate interception plumbing. Research priority is not adoption. The hybrid prototype, experimental recovery fork and Mods have separate immutable source pins in [evidence](evidence.md).

The comparison uses one validated skill with a resource read, a generated file, a pending human decision and a claimed Bash boundary. It must run through the actual Python SDK and chosen engine. A standalone CLI demonstration or hook unit test is insufficient. Replacement Worker and durable approval cases require a Temporal test environment; isolated defer seam checks do not.

The current design remains the defer and synthetic result proposal until a separate integration decision selects a proven alternative. Before executor implementation, revise the specification, this plan and affected work criteria if selection changes execution placement, result delivery or session ownership. Candidate rejection settles only that candidate's scope; it does not prove the retained path.

## Runtime shape

Claude owns skill discovery and the agent loop. Temporal owns orchestration, durable decisions and effect outcomes. Conversation checkpoints, workspace files and protected claims, and Workflow approval/outcome state are separate recovery concerns. They need not use three databases, but each must survive the supported recovery boundary.

The current proposal adds a prepare Activity, a segment Activity that starts an engine subprocess, and effect Activities. Read calls stay inside the engine under confinement. Effect and question calls pause for Workflow dispatch. Definitive results return to the matching original call through the selected result delivery mechanism. Ambiguous Bash parks without another spawn, a model facing uncertainty result or a next model turn.

The `agent` Task Queue handles Workflow Tasks; `segment` and `effect` queues have independent Activity slot budgets. Segment and effect Workers share the supported workspace mechanism and compatible deployment code. Process and filesystem operations stay in Activities, not deterministic Workflow code. A reusable application authored Workflow must use the required registration, policy, security and deployment contract.

The initial implementation landing area is `src/temporalio/claude_agent_sdk/` within this plugin:

| Responsibility | Current proposed landing point | Required boundary |
|---|---|---|
| Exact tool policy and immutable inputs | `_policy.py`, `_models.py` | Default opt out; reject unlisted tools and nested option escapes. |
| Pause identity and confinement | `_defer_hook.py`, `_runner.py` | One paused slot; exact request binding; independent preventive control. |
| Package preparation and manifest | `_workspace.py`, `_activity.py` | Finished copy hash, per run directory and protected claims. |
| Effect execution and result mapping | `_effect.py`, `_workflow.py` | Repeatable files, single attempt claimed Bash and ordered outcomes. |
| Human waits and state | `_workflow.py`, `_models.py` | Signed Updates, durable waits, bounded carried state and replay. |
| Registration and enforcement | `_plugin.py`, Workflow base and inbound interceptor | Required configuration checked before governed execution. |
| Events and visibility | `_events.py` | No raw tool input in events or Search Attributes. |

This is a proposed decomposition, not proof that every module exists. An adopted native execution route needs an explicit replacement decomposition before implementation.

## Stages and gates

The specification's milestone labels map to these stages. They identify technical retirement targets, not private tracker records.

| Milestone | Stage |
|---|---|
| M0 | Preparation |
| M1 | Engine and recovery comparison |
| M2 | Effects and prepared workspace |
| M3 | Decisions, waits and replay |
| M4 | Workspace and process recovery |
| M5 | Hardening and reusable Workflow acceptance |
| M6 | Upstream submission, after final core verification |
| M7 | Harness adapter, after upstream landing |

### Preparation

Resolve the public technical decisions in [deployment prerequisites](work-items.md#deployment-prerequisites): supported storage and volume semantics, effect isolation, gateway responsibilities, reset and uncertainty handling, retention, Search Attributes and deployment order. Record model test prerequisites separately from credentials. Do not publish credential values or private authorization records.

Offline construction can continue only within its existing bounded scope. Paid calls remain disabled until the real model test requirements are satisfied. No documentation change authorizes external contact, dependency promotion or a new integration.

### Engine and recovery comparison

Complete [bounded recovery comparison](work-items.md#bounded-recovery-comparison), then [integration adoption](work-items.md#integration-adoption). Record source verified behavior, fake model results, real model results, unsupported routes and unexecuted cases separately.

Test actual SDK Mods loading, full request identity, native result and error metadata, permission ordering, slash command and model skill invocation, hidden or bundled skills, subagent/background routes, missing interception and hook failures. Failure controls must independently prevent core effect execution; successful interception alone is not a safety proof.

Prove pending approval and exact call recovery on replacement, recorded outcome reuse without another effect, exclusive ownership and orphan process handling. Missing, partial or mismatched session/workspace/manifest/claim state blocks recovery. Crash after an effect and before outcome recording must produce a consistent supported outcome or a blocked recovery. Bash uncertainty always parks.

Finish [real model harness](work-items.md#real-model-harness), [selected result delivery](work-items.md#selected-result-delivery), [preventive control](work-items.md#preventive-control), [validated skill invocation](work-items.md#validated-skill-invocation), [question answer delivery](work-items.md#question-answer-delivery) and [engine compatibility](work-items.md#engine-compatibility). The implemented policy remains in progress until its real engine proving work closes.

Exit gate: the selected mechanism is explicit; actual skill invocation and confinement, exact result delivery, prevention and answer interpretation are proved or contradicted with a recorded design change. Do not start executor work with an unresolved mechanism or unsafe bypass. A candidate source read and an offline test suite cannot satisfy this gate.

Activation is opt in through `tool_policy`; rollback leaves it unset without claiming governed execution.

### Effects and prepared workspace

After the engine exit gate, adoption decision, volume and isolation decisions, complete [prepared workspace and effect identity](work-items.md#prepared-workspace-and-effect-identity), [claimed Bash execution](work-items.md#claimed-bash-execution), [ordered outcomes and refusals](work-items.md#ordered-outcomes-and-refusals), [repeatable file execution](work-items.md#repeatable-file-execution), [tool behavior fidelity](work-items.md#tool-behavior-fidelity), and [process and payload bounds](work-items.md#process-and-payload-bounds).

The current proposal creates a lineage scoped run directory and a Worker owned claims directory outside the effect writable tree. It copies the validated package through a temporary path, renames the finished copy, hashes it and records a manifest generation. Carry package, policy and engine versions and stable pending effect identity. Never infer file restoration from a restored transcript.

Claimed Bash uses one attempt plus both key and ordinal claim guards before spawning. A missing claim directory or arbitrary I/O failure is not safe evidence that an effect never ran. The result mapping distinguishes safe pre execution refusals from tool failures and uncertainty. Enforce the stop before a next segment immediately, not only after signed recovery is implemented.

File effects use explicit repeat and atomic replace protocols. The exceptional self containing Edit retains a single attempt uncertainty path. Native tool adoption must preserve metadata and prove the same supported crash boundaries. Compare success, error, relative path and edit rules against the selected engine.

Exit gate: supported effects have tested results and faults, uncertainty never drives the model forward, process cancellation is preserved, retained version mismatches refuse before execution, and recorded histories replay. Rollback disables new governed execution while preserving parked state, claims and the compatible Worker version. It never reclassifies Bash as a read.

### Decisions, waits and replay

After effect exit and gateway, reset and registration decisions, complete [durable waits](work-items.md#durable-waits), [signed decision enforcement](work-items.md#signed-decision-enforcement), [parked run actions](work-items.md#parked-run-actions), [visibility and registration](work-items.md#visibility-and-registration), [reset identity](work-items.md#reset-identity), and [concurrent and boundary Updates](work-items.md#concurrent-and-boundary-updates).

Updates validate and record promptly; the main Workflow waits. Carry absolute deadlines, unanswered calls, accepted decision IDs, pending actions and park sequence identity across Continue-As-New. Apply an already recorded answer before handover, except that Workflow cancellation takes priority. Do not restart the model against an unanswered pending call.

Token enforcement belongs at the registered inbound boundary, with deterministic validation and replay migration. A handler name or decorator is not authorization. Required registration must fail visibly rather than silently weakening a reused Workflow.

Exit gate: questions and approvals survive Worker loss and repeated handovers, exactly one answer is accepted, direct frontend forgery and subclass bypass are rejected, safe park actions preserve history, and old/new histories replay. Ambiguous Bash recovery remains blocked unless a separately proved safe procedure resolves the uncertainty; claim release and deliberate redispatch are not version 1 features.

### Workspace and process recovery

Complete [effect isolation](work-items.md#effect-isolation), [workspace lifecycle](work-items.md#workspace-lifecycle), [replacement Worker filesystem proof](work-items.md#replacement-worker-filesystem-proof), and [runtime measurements](work-items.md#runtime-measurements).

Protect the package, settings, claims and Worker environment from the effect identity. Contain descendants or name the exact residual. A replacement Worker restores generated files, package, manifest and protected claims independently of conversation state and Workflow decisions. Test real cross container volume semantics, including concurrent exclusive create, or state an explicit untested deployment limit.

The janitor checks Temporal status and run identity, preserves live idle/parked runs, fails safe when status is unavailable, and retains claims through namespace retention. Manifest generation detects restore before the last prepare; it does not establish arbitrary mid run snapshot rollback detection. Keep that limitation visible.

Exit gate: supported filesystem recovery and isolation are proved; any untested environment remains labeled and cannot become a guarantee by wording alone. Record event loop lag, process containment and real model step cost under a stated sample and budget.

### Hardening and reusable Workflow acceptance

Complete [deployment versioning](work-items.md#deployment-versioning), [encrypted payloads](work-items.md#encrypted-payloads), [approval load](work-items.md#approval-load), [session storage conformance](work-items.md#session-storage-conformance), [patch retirement](work-items.md#patch-retirement), [engine promotion](work-items.md#engine-promotion), [shutdown and operational metrics](work-items.md#shutdown-and-operational-metrics), and [application Workflow acceptance](work-items.md#application-workflow-acceptance).

Pinned deployment is the proposed default. Upgrade requires explicit opt in at Continue-As-New and compatible Workers across all three queues. The build identity covers SDK, engine, hook contract and plugin versions. Replay fixtures cover released plugin and enforcement versions; patch retirement is rehearsed before each deploy.

Inspect stored history, not only decoded test values, to prove encryption of Updates and failures. Session storage must be reachable across processes, encrypted at rest, entry UUID deduplicated and fault tested. It does not substitute for workspace restoration or durable outcome records.

The acceptance example uses an application authored Workflow and an unmodified validated skill. It covers a resource read, generated file, signed approval, question/result interpretation and claimed Bash safety. A negative registration/security test refuses execution. This establishes the documented compatibility contract, not arbitrary Workflow compatibility.

Exit gate: repository CI commands pass on required Python versions, replay and upgrade tests pass, real model acceptance stays within its cap, and README limits state actual supported versions, proof gaps, one pause per step, process/volume residuals and no token level replay. Rollback keeps compatible pinned versions and prior release artifacts available.

### Final verification

Complete [evidence and phase reviews](work-items.md#evidence-and-phase-reviews) and [independent final verification](work-items.md#independent-final-verification). Each retained requirement must link to an accessible source or executed proving artifact; source support and runtime support remain different states. All needed technical decisions must be settled for the claimed outcome. A limited documentation alignment check is not this final proof.

Independent verification checks the exact design and repository revisions, transitive implementation impact, source identity, contradictions and replay/effect recovery claims. Material remedies require verification before adoption. A changed design invalidates its earlier verdict. A missing artifact or blocked check is never reported as passing.

The core completion boundary is the evidenced durable skill integration, including its real model proof. Upstream acceptance and the harness adapter are separate later outcomes.

### Upstream and harness adapter

After final core verification, complete [upstream submission](work-items.md#upstream-submission) under repository conventions. Keep the API additive, verify every reviewed commit using the target CI commands and read CI for the exact pushed revision. Submission is not authorized by this plan.

After upstream landing, resolve [harness effect identity](work-items.md#harness-effect-identity) and prove [harness adapter](work-items.md#harness-adapter) separately. Use the harness tool call identity, approval Updates and event vocabulary. Retain the uncertainty park rule. Document that engine reads bypass the harness effect policy. The adapter is optional; rollback removes its import, not the core safety contract.

## Evidence maintenance

For every stage exit, update [specification](spec.md), this plan, [work items](work-items.md) and [evidence](evidence.md) together. Record exact versions, reproducible commands, full results and declared environment limits. Never mark a requirement complete because a related source exists, a candidate was rejected, or a deferred feature was removed from scope. New integration selection requires an explicit criteria disposition before implementation.
