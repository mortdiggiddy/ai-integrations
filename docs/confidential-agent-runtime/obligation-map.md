# Legacy obligation map

Status: PREPARED, 2026-10-26. This map supports the documentation cutover. It does not implement a runtime, approve an unresolved guarantee change, close an old acceptance criterion, or create a new ticket set.

The replacement [specification](spec.md) owns requirements. The [decision register](decisions.md) owns open choices. The [machine readable map](obligation-map.json) preserves exact historical statuses, source row or ticket block digests, and explicit dispositions. The old document tree is archived in place so existing runtime fixtures and evidence links remain available.

## Preservation rule

Every row keeps its original scope and proof limitations. A retained objective is not a completed objective. A replaced mechanism does not retire the objective that required it. An open owner decision defers the decision, not the obligation. Historical retirement means the old source already excluded that mechanism; it is not a new retirement.

For each old ticket, all acceptance criteria remain inspectable in its retained source block. The mapping assigns the whole obligation, including later additions and uncommitted clarifications, rather than only its title. The machine record retains each criterion count and source block digest. This map is not a line by line rewrite of every acceptance criterion. Formal specification work must compare the full source criteria before adopting a narrower replacement.

DONE records retain their exact historical status. OPEN and IN PROGRESS records are inactive historical work after archival, with the unresolved outcome assigned here. No state field in an old ticket is changed by this map. The old phase graph and estimates do not become the new delivery sequence.

## Guarantee changes that remain unresolved

| Concern | Preserved obligation | Open owner |
|---|---|---|
| Original pending call | Exact original success or error recovery is not equivalent to a new model continuation. Native resume cannot silently satisfy it. | BD-01 |
| Independent dispatch | Protected Entity admission, original call identity and reset-safe uncertainty cannot be removed by choosing native built in tools. | BD-02, BD-09 |
| Strict spending | Before-request token and currency admission plus complete cumulative accounting remain a final requirement unless explicitly changed. Monitored experiments are a different approved scope. | BD-03 |
| Accepted progress | Lost acknowledged accepted bytes remain a durability failure. Session, workspace, native metadata and required projections must agree. | BD-04 |
| Trust | Local containers do not prove operator confidentiality or attested dual party key release. | BD-05 |
| Questions and outputs | Fixed tool policy does not answer which sealed questions and outputs may cross party boundaries. | BD-06 |
| Positive child and parallel recovery | The older selected positive outcomes remain open. Unsupported child denial and one serial call are not completion. Optional context processing retains its qualification gates. | BD-08 |
| Retention, reset and integrity | Existing synthetic retention approval and holders remain recorded. Production policy and changed reset/rollback behavior need explicit decisions. Strong malicious operator rollback protection must not be inferred from ordinary generation rejection. | BD-09 |
| Second harness | The broader second harness outcome is deferred until a first complete profile and an accountable second integration exist. It is not retired or satisfied by the initial Claude prototype. | BD-08 |

The old DSR-0.6 and DSR-0.11 decision closures are DONE for their finite approved local configuration and synthetic retention scope. Older navigation still contains OPEN wording; the current owning ticket and its later decision record take precedence. Their runtime, production and portable qualification obligations remain open.

## Coverage

| Family | Rows | Source status |
|---|---:|---|
| DSR work tickets | 61 | Exact owning ticket statuses retained |
| DSR root and phase epics | 9 | Grouping status is retained independently of child status |
| Canonical assumptions A-01 through A-59 | 59 | Historical verified, proposed, open and superseded states remain distinct |
| Candidate assumptions A-60 through A-74 | 15 | Conditional proposal, not adopted qualification |
| Candidate owner decisions | 6 | Legacy BD-1 through BD-6, distinct from new BD-01 through BD-09 |
| Candidate invariants and legacy references | 7 | INV-1 through INV-7 |
| Detailed qualification cases | 15 | Q-1 through Q-15, not executed by this cutover |
| Extracted trust requirements | 8 | R1 through R8 |
| Extracted engine requirements | 11 | E1 through E11 |
| Earlier reuse roadmap | 10 | R01 through R10 remain proposals, not an approved delivery program |

There are 201 mapped rows and 460 retained historical acceptance criteria in the 70 ticket and epic blocks. Identical textual IDs in different families are namespaced by their family. Candidate invariants provide explicit definitions; historical tickets also reference those identifiers. The extracted technical trust and engine source is [consolidated research](evidence/research.md). No private transcript or external working folder is needed to interpret these rows.

## Disposition vocabulary

- **Retain:** keep the objective and applicable proof, with new runtime evidence required.
- **Replace mechanism:** use a different proposed mechanism or sequence while retaining its safety objective.
- **Open decision:** keep the unresolved obligation at the named owner decision.
- **Already retired:** preserve earlier recorded supersession without reviving or proving it.

## DSR tickets and epics

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| DSR-ROOT | Reach a PASS verdict on the durable skill execution design | Replace mechanism | CR-18 | Replace the old phase graph with bounded qualification; preserve evidence and every unresolved guarantee. |
| DSR-P0 | Phase 0: Ground the design and make the owner decisions | Replace mechanism | CR-18, BD-01, BD-02, BD-03 | Carry decision provenance into the new owner register; no old choice approves a changed guarantee. |
| DSR-P1 | Phase 1: Prove the engine mechanism with a real model | Replace mechanism | CR-01, CR-18 | Retain bounded engine evidence at its original pins; new native runtime needs qualification. |
| DSR-P2 | Phase 2: Build and prove the effect executor and workspace | Open decision | CR-08, CR-10, BD-01, BD-02 | Replace segment and effect decomposition only after exact recovery and authority choices. |
| DSR-P3 | Phase 3: Build and prove human decisions, signed tokens and parked runs | Open decision | CR-07, CR-12, CR-14, BD-06, BD-09 | Retain authenticated decisions and safe waits; confidential interaction policy remains open. |
| DSR-P4 | Phase 4: Build and prove isolation and workspace lifecycle | Retain | CR-09, CR-11, CR-16 | Retain isolation, coherent restore, whole execution termination and reference safe cleanup. |
| DSR-P5 | Phase 5: Harden, version and accept the plugin | Open decision | CR-13, CR-17, CR-18, BD-03 | Retain hardening objectives; changed runtime and budget contract need new evidence. |
| DSR-P6 | Phase 6: Pass the independent verification gate | Retain | CR-18 | Formal specification and independent qualification are still required; this cutover is not PASS. |
| DSR-P7 | After PASS: Submit upstream and port to the agent harness | Replace mechanism | CR-06, CR-15, CR-18, BD-08 | Replace plugin-first sequencing with lifecycle reuse; broader harness and child outcomes remain open. |
| DSR-0.1 | Record the official defer and resume protocol | Open decision | CR-01, BD-01 | Exact original call recovery or its explicit replacement must be decided; native resume is not equivalence. |
| DSR-0.2 | Approve the version 1 scope | Retain | CR-10, CR-18 | Preserve approved reduced scope and uncertain Bash refusal; new scope changes need explicit decisions. |
| DSR-0.3 | Rebaseline the specification and plan to the approved version 1 scope | Retain | CR-18 | Retain completed rebaseline evidence for its original contract only. |
| DSR-0.4 | Name the budget owner and credentials for real model runs | Open decision | CR-17, BD-03 | Retain experiment owner, credentials, model and finite allowance gates; strict prevention remains open. |
| DSR-0.5 | Record the outcome of contacting the community plugin author | Retain | CR-18 | Retain recorded contact outcome; it is not upstream acceptance or an agreement for new interfaces. |
| DSR-0.6 | Decide the workspace volume class and the effect isolation level | Retain | CR-08, CR-11, CR-15, BD-02, BD-05 | Retain DONE finite local configuration and holders, not runtime proof or automatic approval of a new profile. |
| DSR-0.7 | Name the owner of the approval gateway | Open decision | CR-07, CR-12, BD-06 | Reconcile gateway ownership and sealed question/output policy; no plaintext human approval default. |
| DSR-0.8 | Decide how a Workflow reset is detected and handled | Open decision | CR-07, CR-10, BD-09 | Preserve partial reset procedure and refusal of uncertain continuation; unresolved action choice stays open. |
| DSR-0.9 | Name who registers Search Attributes and who owns rollout order | Retain | CR-13, CR-18, BD-09 | Preserve visibility registration and rollout responsibilities; exact deployed configuration needs qualification. |
| DSR-0.10 | Record the idempotency key retention window of each keyed service | Already retired | CR-10 | Already excluded keyed service retention mechanism remains historical, not newly implemented. |
| DSR-0.11 | Name the owners of namespace retention and the session store requirement | Retain | CR-08, CR-16, BD-09 | Retain DONE synthetic retention and owners; client production policy and enforcement remain unqualified. |
| DSR-0.12 | Decide which recovery integration the next implementation uses | Retain | CR-01, CR-18, BD-01 | Retain completed Phase 1 proof target choice; it does not select the replacement native recovery guarantee. |
| DSR-1.1 | Build the bounded real model experiment harness | Retain | CR-17, CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.2 | Enforce the tool policy and the preventive backstop in the plugin | Retain | CR-11, CR-12, CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.3 | Prove that a deferred call resumes with a host supplied result on a real model | Retain | CR-01, CR-18, BD-01 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.4 | Prove the preventive backstop and its negative control | Retain | CR-11, CR-12, CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.5 | Validate skill packages and confine reads | Retain | CR-01, CR-11, CR-18, BD-08 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.6 | Prove how a real model reads a deferred question answer | Retain | CR-12, CR-18, BD-06 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.7 | Prove deferral on the minimum and newest engine versions | Retain | CR-01, CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.8 | Settle who declares the handlers and where the token check is enforced | Retain | CR-07, CR-12, CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.9 | Review Phase 1 evidence and decide continue or redesign | Retain | CR-18 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-1.10 | Establish the recovery compatibility boundary of the candidate integrations | Retain | CR-01, CR-18, BD-01 | Retain DONE at its exact original runtime, scope and approved limitations; no new native or confidential qualification is inherited. |
| DSR-2.1 | Prepare the per run workspace, claims directory, manifest, counters and effect identity state | Open decision | CR-07, CR-08, CR-09, BD-02, BD-04 | Retain immutable accepted state, metadata and identity; new capture and authority bindings need decision. |
| DSR-2.2 | Run Bash as a claimed effect with the spawn guard | Open decision | CR-10, CR-11, BD-02 | Do not retire protected Entity scheduling or claimed spawn guard by adopting native tools. |
| DSR-2.3 | Map every effect outcome by the ordered table and the executor fault | Open decision | CR-10, BD-01, BD-02 | Retain honest outcome classes and no continuation for uncertainty; reconcile native execution mapping. |
| DSR-2.4 | Run Write and Edit as repeatable effects | Open decision | CR-08, CR-10, BD-04 | Native file execution replaces proposed wrapper only after postimage and repeat semantics are specified. |
| DSR-2.5 | Run keyed author tools with the idempotency key and retry policy | Already retired | CR-10 | Keyed author tools were already superseded; future selection needs new scope. |
| DSR-2.6 | Match engine behavior by differential test | Retain | CR-01, CR-08, CR-18, BD-01, BD-08 | Keep exact native success/error/metadata and child/parallel differential obligations. |
| DSR-2.7 | Contain process trees, cancellation, shutdown and payload size | Retain | CR-06, CR-11, CR-14 | Keep containment, shutdown, payload and cancellation evidence; local transport does not supply it. |
| DSR-2.8 | Refuse version mismatches with a contract version | Already retired | CR-18 | Additional contract_version field was already superseded; preserve retained compatibility obligations. |
| DSR-2.9 | Review Phase 2 evidence and decide continue or redesign | Replace mechanism | CR-18 | Preserve historical exit criteria; new milestones need their own evidence, not old phase completion. |
| DSR-3.1 | Carry waits and state across Continue-As-New | Retain | CR-14, CR-16, BD-09 | Carry bounded state and unapplied decisions across handover without losing ownership or references. |
| DSR-3.2 | Verify signed tokens in an interceptor | Open decision | CR-07, CR-12, BD-06 | Retain authentication and anti-replay objective; outside plaintext token/handler design is not adopted. |
| DSR-3.3 | Park runs and apply the retry, checkpoint resume and abort actions | Open decision | CR-10, CR-12, BD-06, BD-09 | Retain durable stopped state and authorized safe actions; uncertain Bash action policy remains open. |
| DSR-3.4 | Check Search Attributes at start and discover pending decisions with live output off | Retain | CR-13, CR-12 | Retain discoverability with streaming disabled and content free visibility; metadata never authorizes actions. |
| DSR-3.5 | Prove reset behavior for the lineage id and claim files | Open decision | CR-07, CR-10, BD-02, BD-09 | Preserve first-task/reset/reuse and independent authority tests; no fresh identity can bypass uncertainty. |
| DSR-3.6 | Prove Update behavior at the Continue-As-New boundary and under concurrency | Retain | CR-07, CR-12, CR-14, BD-06, BD-09 | Retain decision race and deduplication across handover on the selected sealed interaction route. |
| DSR-3.7 | Review Phase 3 evidence and decide continue or redesign | Replace mechanism | CR-18 | Replace phase navigation, retain evidence review and explicit residuals. |
| DSR-3.8 | Run redo to repeat or redispatch an unknown outcome on purpose | Already retired | CR-10 | redo and claim release were already superseded and are not revived. |
| DSR-4.1 | Isolate effects at the decided level | Retain | CR-11, CR-05 | Retain actual isolation of effects from credentials, protected state and supervisor controls. |
| DSR-4.2 | Remove run directories safely and detect a restored snapshot | Retain | CR-08, CR-16, BD-09 | Retain preservation-aware cleanup and reference/key/authority retention; no empty repair. |
| DSR-4.3 | Prove accepted checkpoint restoration and independent execution termination | Retain | CR-06, CR-08, CR-09, CR-10 | Keep separate local replacement, original-host/disk loss and live partition/termination oracles. |
| DSR-4.4 | Measure event loop lag, step cost and process containment | Retain | CR-11, CR-13, CR-18 | Measure selected runtime cost and containment; historical per-segment figures are not a forecast. |
| DSR-4.5 | Review Phase 4 evidence and decide continue or redesign | Replace mechanism | CR-18 | Retain independent evidence review; new acceptance does not inherit old phase status. |
| DSR-5.1 | Document and test Worker Deployment rollout and drain | Retain | CR-14, CR-18, BD-09 | Retain compatible versions, rollout/drain and retained-history replay; exact deployment route is open. |
| DSR-5.2 | Prove codec coverage of Update payloads | Replace mechanism | CR-02, CR-13 | Replace outside codec-only placement with sealing before outside processing; still prove every payload and failure path. |
| DSR-5.3 | Prove approvals under subscriber load with live output on | Open decision | CR-12, CR-13, BD-06 | Keep bounded subscriber and decision load proof for the selected confidential interaction path. |
| DSR-5.4 | Prove session store conformance | Retain | CR-08, CR-16, BD-04 | Retain exact accepted bytes, conflicting append refusal, scoped readers and mirror-versus-barrier qualification. |
| DSR-5.5 | Rehearse patch retirement | Retain | CR-14, CR-18, BD-09 | Retain replay/Reset compatibility and evidence-driven patch retirement for supported histories. |
| DSR-5.6 | Run the daily newest engine job and the engine upgrade resume test | Retain | CR-01, CR-18 | Retain exact SDK/CLI qualification and supported upgrade/resume tests; no automatic latest adoption. |
| DSR-5.7 | Prove shutdown, metrics and paid retry rate | Retain | CR-06, CR-13, CR-17 | Retain safe shutdown, diagnostic limits and measured request/retry cost. |
| DSR-5.8 | Prove strict budgeting and real model application acceptance | Open decision | CR-17, CR-18, BD-03 | Strict before-request token/currency enforcement and complete accounting remain unresolved final obligations. |
| DSR-5.9 | Review Phase 5 evidence and decide continue or redesign | Replace mechanism | CR-18 | Retain evidence-based continuation decision; replace old phase navigation. |
| DSR-6.1 | Record evidence and status for every assumption row | Retain | CR-18 | This map preserves all assumption rows; it does not settle or verify them. |
| DSR-6.2 | Confirm that no open decision blocks the stated outcome | Retain | CR-18, BD-01, BD-02, BD-03, BD-04, BD-05, BD-06, BD-07, BD-08, BD-09 | Every applicable owner decision must have an explicit answer before its dependent guarantee is offered. |
| DSR-6.3 | Run the independent verification pass on the evidenced design | Retain | CR-18 | Formal specification and independent review remain later work; no verification PASS is claimed here. |
| DSR-6.4 | Resolve findings and reach a PASS verdict | Retain | CR-18 | Supported findings and proposed remedies need actual reconciliation before a final verdict. |
| DSR-7.1 | Submit the plugin additions upstream | Retain | CR-18 | Upstream contributions are separately scoped; local preparation grants no commit or publication authority. |
| DSR-7.2 | Port the integration to the agent harness | Open decision | CR-06, CR-15, BD-08 | Replace old late glue-only port sequence; optional richer harness features retain explicit qualification. |
| DSR-7.3 | Name the owner of the effect ordinal and key for the harness port | Open decision | CR-07, CR-10, BD-02, BD-07 | Retain one original call/ordinal identity owner and no recomputation for uncertain execution. |
| DSR-7.4 | Select a testable durable child and parallel tool design | Open decision | CR-01, CR-08, CR-18, BD-08 | Positive child and parallel recovery remain selected open outcomes; serial denial is not completion. |

## Canonical assumption rows

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| A-57 | A Mods adapter can load through the selected Python SDK and cover the retained tool paths without bypassing permission, package or read confinement controls. | Open decision | CR-01, CR-18, BD-08 | Mods remain optional and unqualified outside tested lanes; preserve historical rejection and confinement objectives. |
| A-58 | The selected recovery integration can restore an accepted pending main agent request on another Worker while excluding stale owners and surviving CLI processes. | Retain | CR-06, CR-08, CR-09, BD-01 | Retain bounded host recovery evidence and unresolved real host loss; no automatic qualification transfer. |
| A-59 | A selected native tool integration couples original Read/Edit metadata, exact result and required accepted workspace postimage without repeat execution; Context Mode projection preserves raw/native fields and the stored accepted representation. | Retain | CR-08, CR-18, BD-01, BD-04, BD-08 | Retain native metadata/result/postimage and accepted projection association; new route needs evidence. |
| A-01 | The selected original pending recovery adapter returns the exact committed call result or error to the real model without repeating the effect, on qualified SDK 0.2.162 / CLI 2.1.274. Legacy synthetic injection is excluded from governed recovery. | Open decision | CR-01, CR-08, BD-01 | Exact original pending result remains an open guarantee choice; do not equate native continuation. |
| A-02 | The qualified serial route preserves real model mixed call ordering, recorded read denial and original effect outcomes; extra deferred effects in a batch fail closed. | Retain | CR-01, CR-18, BD-08 | Retain serial proof and explicit batch denial limit; positive parallel behavior remains open. |
| A-03 | Independent permission handling must prevent effects missed by interception while preserving deferral. [Scoped ask rules](../../python/claude_agent_sdk/docs/skill-recovery/evidence.md#scoped-permission-backstop-closure-2026-10-05) qualify Write/Edit/Bash and diagnostic skill-granted Writes on the pinned SDK/CLI route. | Retain | CR-11, CR-12, CR-18 | Retain prevention objective and negative controls; qualify the new local runtime rather than inheriting hook proof. |
| A-04 | Protected independent Entity scheduling plus one Activity attempt and retained local claim/heartbeat refusals must prevent a second Bash spawn across outer reset or restored preclaim files. | Open decision | CR-10, BD-02, BD-09 | Protected independent dispatch and retained guards are not retired by native execution. |
| A-05 | Independent authority retains original ordinal/key/input binding; a local ordinal claim adds defense against changed commands but cannot alone establish reset safety after restoration. | Open decision | CR-07, CR-10, BD-02 | Original ordinal/input binding and independent authority remain unresolved for native dispatch. |
| A-06 | A Workflow reset keeps the lineage id, and Workflow Id reuse changes it, because the SDK seeds `workflow.uuid4()` from the original execution run id. | Retain | CR-07, BD-09 | Requalify reset and Workflow ID reuse; no deterministic UUID assumption transfers. |
| A-07 | The starter can mint the lineage id and pass it in the run input, so a reset to the first Workflow Task replays the same id. | Retain | CR-07, BD-09 | Retain starter-owned unique lineage and lost start reconciliation; exact binding awaits specification. |
| A-08 | A Schedule-To-Start timeout parks every retained effect; ordinary repeatable effects record NOT_RUN, special one attempt Edit retains unknown handling, and uncertain Bash never resumes the model. | Retain | CR-10, BD-02, BD-09 | Timeout or missing completion does not prove nonexecution; preserve no uncertain continuation. |
| A-09 | Special Edit whose new text contains old text, with one attempt and explicit unknown handling, avoids double application; other Edit inputs are safe to repeat despite lost heartbeat details. | Open decision | CR-08, CR-10, BD-04 | Edit postimage and repeated application semantics need a native capture contract. |
| A-10 | The retained ordered outcome mapping distinguishes benign executor NotStarted before every claim/spawn, ExecutorFault park, repeatable failure and uncertain Bash park; tool exceptions cannot impersonate safe validation. | Retain | CR-10, BD-01, BD-02 | Retain honest nonexecution/fault/uncertainty distinctions; native error mapping remains open. |
| A-11 | Superseded from version 1: Adding the key to a keyed tool's arguments in the reserved field `idempotency_key` is honored by the external service, so a retry or a replayed call after a reset returns the earlier result. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-12 | Signature verification of the approval token runs inside the Workflow sandbox in an Update validator, using a package outside the sandbox passthrough set. | Open decision | CR-07, CR-12, BD-06 | Retain authenticated interaction; Workflow-side signature placement is not selected for confidential plaintext. |
| A-13 | The token definitions (subject is the decision id or the park id, SHA 256 over canonical JSON, expiry rule, key set, minimum version, per park id) bind a decision so a captured token cannot answer another question or replay against a later park. | Retain | CR-07, CR-12, BD-06 | Retain exact purpose/resource/expiry/replay binding for every permitted sealed decision. |
| A-14 | No documented mechanism lets an Update validator read an authenticated caller identity, and one gateway holding the only credentials that may send Updates is sufficient. | Open decision | CR-07, BD-06, BD-07 | Retain restricted gateway objective; caller identity and protocol authorization need qualification. |
| A-15 | Plugin base plus validated concrete Workflow registration, required validators and one inbound token authority protect only registered handler paths; concrete Pinned configuration and explicit handover are required. | Retain | CR-07, CR-14, CR-18 | Retain registered API enforcement and replay-safe policy; no decorator-only trust assumption. |
| A-16 | Roll out all queues before handover, retain pinned Workers, and validate package_hash, policy_version and engine_version; these checks do not identify every executor only change. | Retain | CR-01, CR-18, BD-09 | Keep exact package/policy/runtime identities and compatible rollout; requalify all changed components. |
| A-17 | The approved first profile uses disposable Linux execution containers and separate trusted service containers, with an external exact-incarnation controller and required container/cgroup confinement. EC2 remains a later portable provider reference. | Retain | CR-11, CR-15, BD-05 | Preserve approved local container profile as development evidence, not an attested confidentiality claim. |
| A-18 | ValidatedSkillPackage admission rejects shell injection, hooks, fork and tool grants; controlled project loading, exact names and native shell disable confine supported invocations and deny hidden, bundled and plugin invocation. | Retain | CR-01, CR-11, CR-12, CR-18 | Keep immutable reviewed skill admission and injection refusal; unrestricted native skills need explicit qualification. |
| A-19 | Shared hook and permission callback confinement denies supported Read/Glob/Grep outside admitted workspace and package roots, including symlink, absolute and parent traversal inputs. | Retain | CR-11, CR-18 | Retain filesystem and read confidentiality objectives; callback checks do not replace OS isolation. |
| A-20 | An approval Update that arrives at a Continue-As-New boundary is delivered to the new run or rejected visibly, and carried `answered_decision_ids` stop a double acceptance. | Retain | CR-12, CR-14, BD-06, BD-09 | Keep decision acceptance and deduplication races across handover. |
| A-21 | Janitor preserves live, parked, reset/replay references, keys, local claims and independent authority; routine cleanup refuses sole-readable required result/postimage destruction. | Retain | CR-08, CR-16, BD-09 | Keep referenced bytes, keys and independent authority through every offered horizon; preserve unresolved sole copy. |
| A-23 | Superseded from version 1: `redo` can remove the claim files through a `release_claim` Activity on the segment queue, dispatch the call at a new ordinal with a new key, reject an ordinal not in `pending_unknown`, redispatch a keyed effect under its stored key, and work when the effect queue is down. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-36 | One owner for internal effect ordinal and claim identity is agreed when the harness owns the loop; external keyed services are deferred from version 1. | Open decision | CR-07, CR-10, BD-02, BD-07 | One call identity owner remains required; ordinary runtime attachment does not decide effect identity. |
| A-45 | Superseded from version 1: A keyed effect's retry horizon (its Schedule-To-Close bound) stays inside the external service's idempotency key retention window. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-48 | Protected independent Entity admission survives outer reset and preclaim restoration; retained local ordinal/key guards remain defense, not portable authority. | Open decision | CR-10, BD-02, BD-09 | Protected Entity or equivalently approved independent authority cannot be removed implicitly. |
| A-49 | Immutable reviewed extra_options and exact extra_args restrictions deny unadmitted permission, tool and interception configuration, including nested mutation. | Retain | CR-11, CR-12, CR-18 | Retain immutable reviewed configuration and refusal of policy override escape paths. |
| A-50 | Worker Versioning is deployed, so the wake check for a changed target Deployment Version is live. | Retain | CR-14, CR-18, BD-09 | Qualify actual Worker deployment mode; it is not supplied by a local runtime transport. |
| A-51 | The janitor can map a run directory to its Workflow and namespace, and a described Workflow whose lineage id differs from the manifest is not treated as the same run. | Retain | CR-07, CR-16 | Keep exact job/lineage/namespace cleanup authorization, including ID reuse and unknown identity. |
| A-52 | Superseded from version 1: monotone claims high-water ordering under shared volume locking. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-54 | Reserved executor and segment refusals reach parked operator state without a model result. | Retain | CR-10 | Keep unresolved executor or segment faults out of model-facing definitive results. |
| A-55 | Superseded from version 1: parked keyed effect duration stays within service key retention before redo. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-56 | Interceptor accept/drop logic and accepted handler reconstruction remain deterministic across plugin versions and replay; validators are conditional, not assumed to run on every replay. | Retain | CR-14, CR-18, BD-09 | Keep deterministic handler reconstruction and mixed version replay proof. |
| A-22 | Recovery eligibility is qualified by exact SDK capability and CLI lane; native deferral success does not imply original pending recovery or safe synthetic resume. | Retain | CR-01, CR-18, BD-01 | Retain exact lane eligibility; native deferral or resume is not proof of original call recovery. |
| A-24 | Credential and quota errors can be classified as non retryable at the segment Activity so the run parks instead of retrying, and Schedule-To-Close of 1 hour with the fork's 10 minute Start-To-Close bounds paid retries correctly. | Retain | CR-10, CR-17 | Retain fault classification and bounded paid retry objectives; do not import untested numeric timeout defaults. |
| A-25 | A real model interprets the recorded AskUserQuestion JSON answers object encoded as text through the selected original pending recovery adapter. | Retain | CR-12, CR-18, BD-06 | Retain bounded question interpretation result; sealed question release remains a separate open decision. |
| A-26 | An actual child tool request fails closed with zero effects; child recovery is unsupported and denied in version 1. | Retain | CR-01, CR-18, BD-08 | Retain child denial evidence; positive child recovery remains open and cannot be satisfied by denial. |
| A-27 | The approved local checkpoint service exercises exact accepted conversation/workspace bytes and metadata on the surviving host. Later portable qualification retains the S3 exact-version reference and restoration on another host with the original disk unavailable. | Retain | CR-08, CR-09, CR-18 | Preserve distinct local restoration and original-host/disk loss acceptance. |
| A-28 | The async segment Activity does not block the event loop, the Python SDK's metric facility emits counters from Workflow code replay safely, and throttled heartbeats on every output line do not create one server call per line. | Retain | CR-13, CR-18 | Measure event loop lag, heartbeat and metric behavior for the new topology; no inherited rate claim. |
| A-29 | The Continue-As-New suggestion fires near 4,096 events with about 12 to 22 events per step, a pending result stays under 2 MB, and External Storage (public preview) plus the 64 KiB output cap keep payloads in bounds. | Replace mechanism | CR-14, CR-18 | Keep bounded history/payload objective; replace unverified fixed event and per-step forecasts with measured limits. |
| A-30 | Upgrade on Continue-As-New (Public Preview) works on the SDK version the plugin pins, with an explicit opt in at handover. | Retain | CR-14, CR-18, BD-09 | Qualify the selected SDK rollout/handover mechanism; preview assumptions and pins are not universal. |
| A-31 | Update arguments and results pass through the Payload Codec like Signals. | Retain | CR-02, CR-13 | Prove sealed content on every relevant message/failure path, not codec placement alone. |
| A-32 | Search Attributes can be registered in every namespace before the first run, and an upsert of an unregistered attribute stalls the Workflow Task with no error to the operator. | Retain | CR-13, CR-18 | Retain declared nonsecret visibility schema and startup validation; qualify actual service behavior. |
| A-33 | The gateway learns of a pending decision through the Query and the `AgentPhase` Search Attribute while live output is off, and the "older than half its timeout" alert reads `OldestPendingAt`. | Retain | CR-12, CR-13 | Retain pending interaction discovery without live streaming under the approved content policy. |
| A-34 | With live output on, about ten concurrent subscribers can starve approvals, and a gateway retry on `RESOURCE_EXHAUSTED` is safe because the question id is the Update id. | Retain | CR-12, CR-13, BD-06 | Retain subscriber/load/decision retry proof; no inherited ten-subscriber capacity assumption. |
| A-35 | Public coordination permits local additive construction; future upstream placement still requires agreement. The known source set contains the implementation inventory. | Retain | CR-18 | Keep historical contact evidence; new source inventory and interface agreement remain separate. |
| A-37 | Object versions, keys, history and independent authority must survive every offered live, parked, reset and replay horizon. The synthetic horizon and holder are approved; real client retention remains a separate owner decision. | Retain | CR-16, BD-09 | Keep approved synthetic policy and holders; production retention and enforcement stay open. |
| A-38 | The approved local checkpoint service and native session adapter must retain exact acknowledged opaque records with authenticated encryption, scoped readers and conditional UUID/head semantics. S3 remains a later portable reference; actual session-store/native compatibility is unqualified. | Retain | CR-08, CR-16, BD-04 | Retain exact acknowledged bytes, scoped readers and conflict refusal; SessionStore mirror is not barrier proof. |
| A-39 | The executor reproduces the engine's Bash, Write and Edit semantics and result text, including relative path differences between `work/` and the run directory. | Retain | CR-01, CR-08, CR-18, BD-01 | Retain native file/result differential fidelity; abandoning wrappers does not settle recovery fidelity. |
| A-40 | The Python Worker shutdown default is zero and the SDK installs no SIGTERM handler, so an explicit graceful shutdown timeout and handler are needed. | Retain | CR-06, CR-11, CR-18 | Qualify whole process shutdown and signal handling in selected runtime; no default-value claim transfers. |
| A-41 | The process tree wait and group kill contain an effect's children, and a daemonized child or a partitioned host remain documented residuals. | Retain | CR-06, CR-11 | Retain whole descendant containment and live partition tests; cooperative cancellation is not a death witness. |
| A-46 | A Reset of a closed run replays its patch and deprecation markers against the deployed code, so a patch is removed only when no replayable run carries its marker. | Retain | CR-14, CR-18, BD-09 | Retain compatibility across retained replay/Reset histories and explicit patch retirement. |
| A-47 | Superseded from version 1: The keyed effect retry policy (SDK defaults, a 10 minute Schedule-To-Close bound, `ToolDefinitiveError` non retryable at the throw site) suits the tools authors write. | Already retired | CR-10, CR-18 | This mechanism was already superseded by the approved legacy scope. Preserve that status; future use requires explicit new selection. |
| A-53 | Executor exception wrapping preserves cancellation and safe pre claim versus post claim failure classification. | Retain | CR-10 | Retain pre/post admission distinction and cancellation preservation in native error handling. |
| A-42 | Stamping `wait_started_in_run` at each run's wait entry, with a cooldown of one wake interval, prevents a handover on every wake. | Retain | CR-14, BD-09 | Retain stable wait deadlines and bounded rollover; exact timer/cooldown numbers remain selected-profile choices. |
| A-43 | Per step cost of 0.7 to 0.9 seconds and about 270 MB per segment, measured with an instant local model, approximates real cost. | Replace mechanism | CR-18 | Measure actual selected runtime cost; old per-segment latency and memory are historical only. |
| A-44 | The selected controlled project loading and runner configuration invoke only admitted exact Skill names; starting slash dispatch refuses before startup and AskUserQuestion defers under pinned default mode. Native Bash effects always defer. | Retain | CR-01, CR-12, CR-18 | Keep controlled native invocation and policy enforcement; qualify local native tool execution as a new lane. |

## Conditional candidate assumption rows

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| A-60 | Selected accepted-head/opaque blob or bounded-history/store authority and exact conditional SDK adapter preserve ordered ACKed prefix | Open decision | CR-08, BD-04 | Retain accepted ordered prefix and acknowledged-data loss obligation; choose actual storage acceptance mechanism. |
| A-61 | Selected cold bundle/reattachment preserves native workspace metadata and protected spawn claims | Retain | CR-08, CR-09, CR-11 | Keep metadata-complete workspace and guard restoration; no independent authority repair from files. |
| A-62 | Independent Entity Workflow/unique store retains stable intent across outer reset, handover and supported rollback | Open decision | CR-10, BD-02, BD-09 | Independent intent across reset, handover and supported rollback remains an open mechanism choice. |
| A-63 | Sealed receipt and orphan reconciliation refuse inconsistent cross store states | Retain | CR-08, BD-04 | Keep coherent receipt and orphan handling; cross-store transactions are not assumed. |
| A-64 | Supervisor verifies prior execution termination before replacement | Retain | CR-06, CR-09, CR-11 | Keep independently reconciled old execution exclusion before replacement. |
| A-65 | Effects cannot access protected keys/state and cannot survive teardown | Retain | CR-11, CR-05 | Keep effects isolated from protected keys, state and control capabilities. |
| A-66 | Signed decisions/dedup/cancellation survive recovery/handover | Retain | CR-07, CR-12, CR-14, BD-06 | Keep authenticated decisions and deduplication across recovery, cancellation and handover. |
| A-67 | Qualified retained versions support compatible original pending recovery | Open decision | CR-01, CR-18, BD-01 | Retain exact recovery compatibility requirement until native continuation choice is explicit. |
| A-68 | Retention/reset policy retains authority throughout every recoverable window | Retain | CR-16, BD-09 | Retain authority/object/key lifetime through every supported recovery window. |
| A-69 | Chosen workload/objectives fit bounded history/storage/cleanup capacity | Retain | CR-13, CR-14, CR-18 | Select bounded workload and measured service objectives; no invented production capacity. |
| A-70 | Optional confidential lane preserves key/freshness and recovery boundaries | Retain | CR-05, CR-08, BD-05, BD-09 | Confidential mode is now a project objective; specific key/freshness/rollback promises need qualification. |
| A-71 | Chosen trusted Mod and exact required hooks load in production SDK with package/child restrictions intact across reloads | Open decision | CR-01, CR-11, CR-18, BD-08 | Optional trusted Mods require actual loading and confinement proof if selected; not a new prerequisite. |
| A-72 | Independent controller/capability boundary prevents native and direct plugin effects when a required bridge fails or disappears | Open decision | CR-11, CR-12, BD-02, BD-08 | Required bridge fail-open prevention remains an activation condition for any selected Mod lane. |
| A-73 | Native projection and suspension preserve complete typed original pending identity/outcome through selected SDK adapter | Open decision | CR-08, CR-18, BD-01, BD-08 | Keep typed original pending identity and projection fidelity if this optional route is selected. |
| A-74 | Optional accepted complete response escrow has lossless effective request/outer stream/trajectory and fenced durable recovery | Open decision | CR-08, CR-17, BD-01, BD-04, BD-08 | Complete model response escrow remains optional; no new promise of saved model requests is adopted. |

## Conditional candidate owner decisions

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| BD-1 | Which failures resume or park and what accepted state loss contract applies? | Open decision | BD-01, BD-04 | Original failure/loss contract remains open; new design must preserve or explicitly replace it. |
| BD-2 | Which substrate/storage/isolation and named security/deployment owners apply? | Open decision | BD-02, BD-05, BD-07 | Keep selected local owner/configuration evidence; new authority, substrate and deployment binding require decisions. |
| BD-3 | What retention/reset/replay/backup restore policy applies? | Open decision | BD-09 | Preserve approved synthetic horizons and holders; offered Reset, backup and production policies remain explicit. |
| BD-4 | What workload/deadlines/payload bounds and measured SLOs apply? | Open decision | CR-13, CR-14, CR-17 | Select finite workload, deadlines and measured objectives before affected execution. |
| BD-5 | Is confidential execution required against which adversary? | Replace mechanism | CR-02, CR-04, CR-05, BD-05 | Confidentiality is now required as an outcome; concrete adversary/deployment/key qualification remains open. |
| BD-6 | Adopt protocol extension/proposed rigor tier and which optional Mods lanes, revise scope or reject? | Open decision | BD-01, BD-02, BD-08, CR-18 | The old distributed protocol was conditional; cutover does not adopt its mechanisms or optional lanes. |

## Candidate invariants and historical references

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| INV-1 | Failure model | Retain | CR-06, CR-09, CR-10, BD-01 | Retain explicit loss, uncertainty and cancellation contract; old step boundaries require reconciliation. |
| INV-2 | Worker and task queue topology | Replace mechanism | CR-02, CR-03, CR-06, CR-15 | Replace segment/effect Worker topology with outside control and inside native runtime. |
| INV-3 | Workflow and activity modeling | Retain | CR-01, CR-12, CR-14 | Retain deterministic outside orchestration and native policy; no confidential plaintext in Workflow code. |
| INV-4 | Long running behavior | Retain | CR-14, CR-16, BD-09 | Retain bounded handover, decisions and referenced state. |
| INV-5 | State ownership and idempotency | Retain | CR-07, CR-08, CR-10, BD-02, BD-04 | Retain authority and state distinctions; native runtime does not decide acceptance or independent dispatch. |
| INV-6 | Observability and service levels | Retain | CR-13, CR-18 | Retain content-safe observability and measured objectives. |
| INV-7 | Security and privacy | Retain | CR-04, CR-05, CR-11, CR-12 | Retain confidentiality, identity, package and execution isolation. |

## Detailed qualification cases

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| Q-1 | A nominal processor changes workspace or external systems | Retain | CR-11, BD-08 | Retain immutable processor input and forbidden mutation/egress controls if artifact processing is selected. |
| Q-2 | Index rebuilding silently changes accepted model input | Retain | CR-08, CR-16, BD-08 | Keep raw and accepted projections independent of disposable indexes. |
| Q-3 | Wrong identity/status or missing native bookkeeping advances a pending call | Open decision | CR-08, BD-01, BD-04 | Retain exact original success/error identity and metadata qualification. |
| Q-4 | Missing projection hook exposes excluded output | Retain | CR-08, CR-12, BD-08 | Missing required projection cannot disclose excluded output or silently continue. |
| Q-5 | Source adapter flags are mistaken for host enforcement | Retain | CR-01, CR-11, CR-18 | Source flags are not installed prevention proof; preserve actual positive and disabled control tests. |
| Q-6 | Artifact labels or paths allow cross-session exposure | Retain | CR-04, CR-07, CR-16 | Retain exact scoped reader authorization and cross-session denial. |
| Q-7 | Component import starts executor, telemetry, healer or config mutation | Retain | CR-11, CR-18 | Retain dependency/startup, network, configuration and installation surface qualification. |
| Q-8 | Outer Activity retry repeats hidden inner mutation | Retain | CR-10, BD-02 | Retain lost completion and physical invocation counter proof; no hidden retry bypass. |
| Q-9 | Remote submit reply loss duplicates jobs or loses completed output | Retain | CR-06, CR-10, BD-02 | Lost submit/result replies reconcile the same original operation; optional keyed service scope stays conditional. |
| Q-10 | Local replacement retains transcript but loses file/claim or descendant consistency | Retain | CR-06, CR-08, CR-09 | Keep local replacement and whole execution cleanup oracle. |
| Q-11 | Local-only state is mistaken for portable recovery | Retain | CR-08, CR-09 | Keep original host/disk inaccessible and accepted-data loss failure oracle. |
| Q-12 | Two partitioned live executions act concurrently | Retain | CR-06, CR-09, CR-11 | Keep live partition and lost termination receipt reconciliation before replacement. |
| Q-13 | Unresolved local postimage is destroyed during planned cleanup | Retain | CR-08, CR-16 | Routine cleanup must retain required sole-readable local outcome/postimage. |
| Q-14 | Logical authority can be reset into an empty reusable permission | Open decision | CR-10, BD-02, BD-09 | Independent authority reset/recreation must not produce reusable dispatch permission. |
| Q-15 | Unnecessary fork creates unowned maintenance or improper copying | Retain | CR-01, CR-18, BD-08 | Retain exact selected source/license/maintenance review; optional components require a concrete reuse need. |

## Extracted trust requirements

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| R1 | Service history and object storage hold ciphertext. | Retain | CR-02, CR-13 | Keep encryption before outside handling, including failures and content export. |
| R2 | Recover on a replacement host without accepted data loss. | Open decision | CR-08, CR-09, BD-01, BD-04 | No-loss meaning and acknowledged progress boundary remain decisions, not silently reduced native continuation. |
| R3 | The client cannot inspect protected skill material. | Retain | CR-04, CR-12 | Keep output release and separate reader policy; model access is a separately declared boundary. |
| R4 | Operator administrators cannot inspect client code or conversation. | Retain | CR-02, CR-04, CR-11 | Keep all confidential plaintext processing inside the approved trusted runtime. |
| R5 | Neither party can decrypt protected material alone. | Retain | CR-04, CR-05, BD-05 | Keep mutual approval and gated key release; concrete scheme needs qualification. |
| R6 | Operator-controlled environment cannot steer or observe protected execution. | Retain | CR-05, CR-11, CR-12, CR-13 | Keep approved launch policy, restricted administration, egress and telemetry. |
| R7 | Protection from the cloud hypervisor is a distinct stronger profile. | Open decision | CR-05, BD-05 | Do not claim this from protected VM attestation alone; select only when threat scope requires it. |
| R8 | Model-provider plaintext access is a separate inference trust boundary. | Open decision | CR-04, BD-05 | External native model inference does not hide prompts from that provider; stronger inference remains separate. |

## Extracted engine requirements

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| E1 | All durable content must pass through a protected persistence boundary. | Replace mechanism | CR-02, CR-08 | Replace payload-only mechanism with encrypted accepted state; native local files are not durable until accepted. |
| E2 | Compose payload and failure protection with execution. | Retain | CR-02, CR-13 | Preserve converter/failure coverage while moving content sealing inside trust boundary. |
| E3 | No confidential content in identifiers, visibility, logs or metric labels. | Retain | CR-13 | Keep all plaintext metadata surfaces within explicit content policy. |
| E4 | Bind workspace capture to the corresponding accepted engine state. | Open decision | CR-08, BD-04 | Per-step hook is not assumed available; capture boundary must be selected and qualified. |
| E5 | Distinguish did not run, completed and may have run outcomes. | Retain | CR-10, BD-01, BD-02 | Keep uncertainty visible to the service; no fabricated definitive model result. |
| E6 | Support headless execution and constrained egress. | Retain | CR-01, CR-11 | Keep native SDK route and trusted configuration; no required interception proxy follows. |
| E7 | Authenticate sealed inbound content and bind job and sequence. | Retain | CR-07, CR-12, BD-07 | Keep client input identity and replay refusal; exact wire/key protocol remains open. |
| E8 | Confidential tool decisions use fixed local policy rather than content-revealing human approvals. | Retain | CR-12, BD-06 | Retain permitted sealed questions and output release as separate decisions. |
| E9 | Fence accepted checkpoints by current generation and predecessor. | Retain | CR-07, CR-08, BD-04, BD-07 | Keep stale acceptance refusal; exact Temporal Update shape remains proposed. |
| E10 | Capture only at a consistency boundary accounting for every writer. | Retain | CR-08, CR-11, BD-04, BD-08 | No post-tool copy or background writer assumption supplies a coherent accepted state. |
| E11 | The trusted runtime seals output, authenticates input, enforces policy, validates restore and confines Bash. | Replace mechanism | CR-02, CR-03, CR-07, CR-08, CR-11, CR-12 | Replace dropped-SDK/Mod topology with native local SDK candidate; keep plaintext invariant. |

## Earlier reuse roadmap

| Legacy ID | Obligation | Disposition | New owners | Treatment |
|---|---|---|---|---|
| R01 | Pin integration baseline and preserve compatible existing provider behavior. | Replace mechanism | CR-15, CR-18 | Keep pinning and compatibility; old PR routing import is no longer a mandatory prerequisite. |
| R02 | Add explicit placement and capability checks before allocation. | Retain | CR-03, CR-15 | Keep the bounded generic external runtime contribution. |
| R03 | Harden controller identity, retries, transitions, readiness, cleanup and history. | Retain | CR-06, CR-14, CR-16 | Retain affected lifecycle outcomes; select narrowly rather than requiring all hardening before first mode. |
| R04 | Compose controller generation with a conversation adapter and runtime bridge. | Replace mechanism | CR-06, CR-07, CR-14, BD-07 | Keep single ownership; Python client and ordinary remote SDK bridge are not private prototype prerequisites. |
| R05 | Qualify one attested provider and locked supervisor image. | Retain | CR-05, CR-11, BD-05 | Keep final confidential activation gate; local container proof is not attestation. |
| R06 | Publish and restore coherent encrypted accepted recovery state. | Retain | CR-07, CR-08, CR-09, BD-04 | Keep original host loss, late upload, conflict and corrupted state refusal. |
| R07 | Qualify native execution adapters and required child behavior. | Open decision | CR-01, CR-08, CR-18, BD-01, BD-08 | Prefer one native SDK route; optional turn/Mods adapters and positive child/parallel outcomes remain open. |
| R08 | Complete gateway, fixed policy, question and output controls. | Retain | CR-04, CR-07, CR-10, CR-12, CR-13 | Keep unauthorized zero-effect, sealed sequencing and content release tests. |
| R09 | Deliver reference application, recovery evidence and operational contract. | Retain | CR-06, CR-09, CR-13, CR-16, CR-18 | Keep end-to-end qualified profile and measured limits before confidentiality claims. |
| R10 | Qualify another agent harness and optional service facade using the same lifecycle and recovery contracts. | Open decision | CR-15, CR-18, BD-08 | Retain as a later activation outcome after the first complete profile and a concrete second harness owner; not satisfied by first Claude prototype. |

## Evidence and completion limits

The map was derived from all owning phase files and epics, the canonical assumption table, conditional candidate assumptions and decisions, explicit candidate invariant headings, and the detailed Q case table. It also extracts the technical trust requirements and the earlier reuse roadmap. Source identities in the JSON describe the captured input, not a claim that historical documents are current contracts.

The mapping contains no new technical product claim requiring a new runtime experiment. It preserves requirements and proposed mechanisms as obligations. It does not validate those mechanisms, classify a failed experiment as passed, or satisfy the later formal specification and independent review.

Before replacing an old acceptance criterion, the formal specification pass must record the owner decision or requirement that justifies the change, its failure consequence, and its new observable proof. An unresolved decision may block only the guarantee that depends on it; it does not reopen completed historical work or prohibit independent credential free preparation.
