# Recoverable skill execution work items

These work items implement the [specification](spec.md) through the [plan](plan.md). [Evidence](evidence.md) owns public source pins, reported test results and proof limits. Descriptive headings are stable dependency anchors. This is the canonical technical work list, not an export of a private tracker or authorization log. Estimates are omitted; the bounded outcomes and acceptance checks govern completion.

`IN PROGRESS` means construction or research exists but acceptance remains incomplete. `OPEN` means completion is not established. Checked criteria identify only the bounded offline result stated beside them. Core completion excludes upstream acceptance and the separately proved harness adapter. Each stage requires its [evidence review](#evidence-and-phase-reviews) before the next dependent stage starts.

## Deployment prerequisites

Status: OPEN

Dependencies: [specification](spec.md), [plan](plan.md#preparation).

- [ ] State the selected volume class, workspace preservation mechanism, exclusive create semantics, supported host topology and effect isolation level. Name responsible roles without publishing personal authorization records.
- [ ] State gateway signing, key rotation, minimum token version, caller credential control and implementation language. Define pending decision expiry while the gateway is unavailable.
- [ ] Define reset detection without treating a changed claim Run Id alone as reset proof. State how investigation checks earlier outcomes, surviving processes, workspace and claim integrity; unresolved integrity or Bash uncertainty blocks continuation.
- [ ] Define starter supplied lineage uniqueness, Search Attribute registration before first execution, Worker Versioning availability and rollout/drain ownership across all queues.
- [ ] Define namespace retention and shared encrypted session storage responsibilities. Unknown retention keeps claim files; dropped session writes cannot silently publish a wrong checkpoint.
- [ ] State prerequisites for model testing: credential provisioning outside the repository, allowed model identifiers, per run and aggregate spend caps, and a stop rule. Do not include credential values or grant execution permission in this document.

## Real model harness

Status: IN PROGRESS

Dependencies: model testing requirements in [deployment prerequisites](#deployment-prerequisites). Offline construction exists; real model completion remains blocked.

Inspection checkpoint (2026-10-02): `tests/helpers/offline_harness.py` always refuses paid execution and patches the SDK stream, version query and checkpoint. Its configuration contains per run USD/token caps and a credential environment reference, but no approved model allowlist, phase ledger or preventive token enforcement. The runner forwards `max_budget_usd` per segment; this does not establish a cap across resumed segments or the phase. Complete the following bounded harness work before selected result delivery uses a real model. The passing deferred checkpoint feasibility check does not change this gate.

- [x] Offline harness tests cover records, overlapping run refusal and paid execution refusal; simulated versions, usage, transcript and checkpoint are not runtime proof. See [evidence](evidence.md).
- [ ] Refuse real model startup when credential, cap or model identifier is absent; a deliberately low cap stops with a non passing outcome.
- [ ] Enforce the approved exact model allowlist and explicit credential route without ambient provider fallback. Keep paid execution disabled until separate execution authorization and verified enforcement exist.
- [ ] Reserve and reconcile per run and phase budgets across resumed segments, retries and overlapping processes. Incomplete usage or a lost process must not release an unresolved reservation or permit an unaccounted continuation. Keep Phase 5 accounting separate.
- [ ] Verify preventive token limits before provider requests, including resumed requests, rather than treating result usage as enforcement. If the selected route cannot meet the approved token boundary, stop for an explicit budget design decision before paid execution.
- [ ] A bounded real run records SDK wheel, printed CLI version, model, usage, cost and full transcript without credential values. Observed token counts after a result are not a preventive token cap.
- [ ] Record minimum and selected newest engine lanes and any explicit cooldown exception. Run required default tests with no model credentials.

## Policy and pause identity

Status: IN PROGRESS

Dependencies: [specification](spec.md). Construction precedes the preventive control tests; real engine completion also requires [preventive control](#preventive-control), which is an exit check rather than a construction blocker.

- [x] Offline policy tests cover exact retained names, immutable input/digest binding, option snapshots and legacy behavior when the option is unset. See [evidence](evidence.md).
- [x] The implemented hook denies unvalidated Skill, binds the first paused request to ID, exact name and canonical inputs, re defers an identical reannouncement without replacement, denies every different call after pause and every call after stop, and rejects mismatched checkpoint requests in offline tests.
- [x] Offline option tests put effects in offered tools but outside `allowed_tools`, pin `default` permissions, reject unreviewed or nested option escapes, and cover the effect observation detector. These are not real engine prevention results.
- [ ] Complete the real engine permission, missing interception and result delivery proofs linked below before marking the policy complete. Effects cannot complete through the policy until its executor or an explicitly adopted alternative exists.

## Bounded recovery comparison

Status: DONE (2026-10-02, bounded research disposition)

The [approved acceptance disposition](comparison-disposition.md#acceptance-map) closes bounded research through local proof, candidate rejection, route exclusion and needs host implementation outcomes. Permission/alternate routes, original disk loss, complete skill composition and general cancellation remain unexecuted and required at their engine, filesystem/session, application and process/shutdown gates. Completion does not establish production compatibility.

The [second host contract batch](evidence.md#bounded-host-contract-comparison-2026-10-01) passed local concurrent admission and teardown gating, controlled owned descendant cleanup before replacement, eight durable native Bash/missing-state park cases, and disposable signed approve/reject integrity across replacement. Accounting alone still allowed an orphan error fallback/model continuation. The host adapters, local disk faults and explicit cryptography passthrough constrain these findings; distributed lease/fencing, spontaneous loss supervision, arbitrary descendant containment, general filesystem/claim restoration, production gateway/registration and complete native skill/permission coverage remain open. The checked comparison criteria below record approved research dispositions; no broad runtime requirement passes from these local results.

The existing dependency batch is [recorded in evidence](evidence.md#bounded-comparison-on-the-existing-dependency-lane-2026-10-01), followed by the [bounded native file comparison](evidence.md#bounded-native-file-replay-comparison-2026-10-01). The latter verifies recorded native success/error reuse and an unpublished Edit replay after restoring a single file snapshot, with two physical Edit invocations and one committed outcome. General filesystem/claims, production ownership and process supervision remain open. The [experimental main comparison](evidence.md#bounded-experimental-main-recovery-comparison-2026-10-01) verifies four replacement Worker MCP outcome/approval cases and six SDK preflight refusals in a disposable installation. Concurrent completed resumes launched two CLIs, and Worker losses left orphans requiring harness cleanup. That earlier batch did not prove actual Bash effects, durable parking, signed decisions or general filesystem/claims recovery; the host batch above adds only its stated local proof. Research status does not authorize adoption or executor implementation.

Dependencies: [real model harness](#real-model-harness) for paid cases and [deployment prerequisites](#deployment-prerequisites) for required test controls. Offline checks require no paid call.

- [x] Record ordered comparison, immutable builds, loading, commands and every case disposition in the approved map.
- [x] Reject Mods for the tested invocation and its five unexecuted hook negatives through the explicit rejection branch; other builds remain unexecuted.
- [x] Record bounded call/result/error identity recovery and SDK versus host refusal controls; exclude unsupported pending children and alternate transport/fork routes.
- [x] Record permission/mixed/skill/child/plugin/background routes as unexecuted and excluded from comparison compatibility. Actual prevention and confinement remain required before engine exit.
- [x] Record pending approval replacement, failed SDK ownership/orphans, local host lease/control-loss proof and accounting only failure; production host implementation remains required.
- [x] Record bounded native file gap and actual Bash uncertainty park without claiming general filesystem/claims restoration.
- [x] Assign original disk loss to replacement Worker filesystem proof and session storage conformance; retain general cancellation/graceful suspension in process/shutdown proofs.
- [x] Retain the complete validated skill scenario in validated skill invocation/application Workflow acceptance; individual fixtures do not prove it.
- [x] Record selected Phase 1 seam and A-57/A-58/A-59 dispositions without unsupported runtime closure.

## Integration adoption

Status: DONE (2026-10-02, Phase 1 proof target only)

The [approved decision](comparison-disposition.md#options-and-recommendation) selects experimental main recovery for Phase 1 proof with exact pins and mandatory host controls. Dependency promotion and production/native effect adoption remain gated; the implemented baseline is unchanged.

Dependencies: [bounded recovery comparison](#bounded-recovery-comparison).

- [x] Record retain, adopt or redesign with a reason for every unsupported/rejected candidate; research priority alone does not select the implementation.
- [x] State exact supported versions, released versus experimental API status, integration boundary and any separate dependency promotion prerequisites.
- [x] Allocate conversation, workspace/claims and approval/outcome state plus replacement ownership/orphan responsibilities without claiming local Mods storage is distributed atomicity.
- [x] Preserve native skill execution in application authored Workflows under required registration/security/policy; the [harness adapter](#harness-adapter) remains separate.
- [x] Update spec, plan and affected acceptance criteria before executor work. Give each previous result delivery criterion an explicit retained or replaced disposition, preserve Bash uncertainty blocking, and do not reinterpret old proof as evidence of a new mechanism.

## Selected result delivery

Status: IN PROGRESS (2026-10-02, rebaseline and offline feasibility only)

[Deferred checkpoint feasibility](evidence.md#deferred-checkpoint-feasibility-2026-10-02) passed in separate author/lead runs with unchanged actual Write transcripts. This establishes the callback seam before deliberately blocked transport. All retained real model result delivery criteria below remain unchecked; the in-memory result/store fixture does not satisfy external Activity, resumed model or production recovery acceptance.

Dependencies: [integration adoption](#integration-adoption), [real model harness](#real-model-harness), [policy and pause identity](#policy-and-pause-identity).

- [ ] Before real model execution, establish with an actual deferred checkpoint and pinned experimental SDK that the accepted ID/name/input/transcript UUID reaches recovery before transport startup. Do not edit the transcript to manufacture an unresolved call. Failure stops for redesign.
- [ ] Prove deferred Write creates no engine file before accepted segment commit; external effect Activity success is recorded once and exact recovery to the original pending call executes no additional effect.
- [ ] Prove deferred Bash creates no engine marker before external dispatch; deliver a recorded error unchanged, reject without execution and preserve ambiguous park without result/model continuation.
- [ ] Replace candidate synthetic injection/resume hook assertions with callback-before-transport, serial recovery and full identity/state refusal. Preserve the old synthetic path as baseline regression only.
- [ ] Retain two effects without silent loss, read before effect and visible denial after pause; record real model response or prompts tried if the required shape is not emitted.
- [ ] Retain complete transcripts, exact SDK/CLI/model versions, tool counts, filesystem checks and per run/aggregate spend. Harness and budget gates remain mandatory; cap stop is non passing.
- [ ] Repeat decisive cases on the production integration before completion; fixture/spike evidence does not close real model acceptance. Failures stop executor entry pending redesign or proved fallback.
- [ ] Separate official resume scope from experimental recovery; no released skill/batch/permission support is inferred.

## Preventive control

Status: OPEN

Dependencies: [policy and pause identity](#policy-and-pause-identity), [real model harness](#real-model-harness), selected route from [integration adoption](#integration-adoption).

- [ ] With a no decision hook and independent control present, no file/effect marker is created and permission refusal is observed. Removing the control makes the intended negative test fail.
- [ ] For adopted Mods, rerun missing/disabled/throwing/over budget/malformed controls across offered child and plugin routes. Explicitly exclude unsupported routes rather than infer global coverage.
- [ ] Observe read only Bash under `default`; if it bypasses control, test a scoped denial or exclude Bash until a supported prevention mechanism exists.
- [ ] Test skill permission grants and each pinned option escape, including raw flags and nested caller mutations. Every permitted option leaves the prevention tests passing.
- [ ] If prevention fails, record the weaker detected violation boundary and redesign the affected guarantee before continuing. A post execution detector never counts as prevention.

## Validated skill invocation

Status: OPEN

Dependencies: [policy and pause identity](#policy-and-pause-identity), [real model harness](#real-model-harness).

- [ ] Reject shell injection, skill hooks, `context: fork` and `allowed-tools` grants with named reasons; accept a clean supported package and publish unsupported frontmatter.
- [ ] Prove actual model and slash command invocation resolves to the validated package. Hidden, bundled, additional package and starting prompt routes must refuse or be independently confined. Unknown names refuse before model execution; startup inventory is diagnostic only.
- [ ] Prove controlled project loading through the chosen `setting_sources`, and distinguish default query behavior, user sources and the `plugins` option. The original explicit empty source list is not proof of package loading.
- [ ] Deny Read, Glob and Grep outside supported roots through symlinks, absolute paths and parent patterns. Verify actual tool argument schemas and shell disable behavior rather than assuming setting names.
- [ ] Record subagent pause/fail closed behavior and offered Agent denial with zero unrecorded effects. Any adopted integration preserves restrictions or excludes unsupported child recovery.

## Question answer delivery

Status: OPEN

Dependencies: [selected result delivery](#selected-result-delivery), [policy and pause identity](#policy-and-pause-identity), [real model harness](#real-model-harness).

- [ ] Prove `AskUserQuestion` availability and pause under the chosen mode/callback configuration.
- [ ] A real model receives three answer sets, including supported single/multiple choice cases, with the delivered answer and next model action recorded for each.
- [ ] If structured answers are misread, run the same cases with the plain text fallback and record the selected answer form. All runs remain within the configured cap.

## Engine compatibility

Status: OPEN

Dependencies: [selected result delivery](#selected-result-delivery), [preventive control](#preventive-control), [question answer delivery](#question-answer-delivery).

- [ ] Run selected production integration result, permission, batching, confinement and question proof cases on minimum and selected newest engines, plus the legacy suite. Record wheels, printed versions and any missing lane.
- [ ] Record whether each engine honors post pause denial; a failing minimum requires an explicit version floor/design decision, not silent promotion.
- [ ] Close engine stage only after the comparison and adoption decision plus required real model proofs. Contradictions require a recorded design change before executor entry.

## Prepared workspace and effect identity

Status: OPEN

Dependencies: engine stage exit, [integration adoption](#integration-adoption), volume/isolation in [deployment prerequisites](#deployment-prerequisites).

- [ ] Prepare the lineage scoped run directory, Worker owned claims outside the effect writable tree, finished package copy, manifest and generation. Repeat prepare verifies a completed directory; crash before rename never leaves an accepted partial package.
- [ ] Hash sorted relative paths, normalized modes and file bytes; reject symlinks. Per run `cwd` reaches engine, session key, copy and mismatch checks without event loop blocking or shared session identity.
- [ ] Store lineage, advancing ordinal and canonical effect key before dispatch; compute a pending key once, preserve it on retry/handover and replay, and separate Workflow Id reuse.
- [ ] Carry retained package/policy/engine versions and manifest generation. Present conversation history with missing files cannot satisfy workspace restoration.
- [ ] All default tests run without credentials. The selected workspace mechanism and supported recovery boundary are explicit in manifest assertions.

## Claimed Bash execution

Status: OPEN

Dependencies: [prepared workspace and effect identity](#prepared-workspace-and-effect-identity).

- [ ] Spawn once with `maximum_attempts=1`, protected key and ordinal claims created before the spawn record/spawn, and explicit timeout, heartbeat, cancellation and output limits.
- [ ] Refuse an existing claim, preserved spawn record or later attempt. Effect identity cannot create/change/delete either claim or its directory. Missing directory or arbitrary I/O failure spawns nothing and is not misclassified as duplicate evidence.
- [ ] Timeout, lost Worker, post claim failure, exhausted attempt and Activity reset never spawn twice and block the next model turn. The reset test does not rely on `attempt`, which can return to one.
- [ ] A different command at an occupied ordinal after Workflow reset refuses and parks. State the claim integrity and supported volume assumptions plus partitioned host/daemon residuals.
- [ ] Reject background execution and use the selected environment allow list. Claim removal and deliberate redispatch remain outside version 1.

## Ordered outcomes and refusals

Status: OPEN

Dependencies: [claimed Bash execution](#claimed-bash-execution), [prepared workspace and effect identity](#prepared-workspace-and-effect-identity).

- [ ] Table driven Workflow tests exercise every retained outcome and overlap precedence in the spec. Safe repeatable Schedule-To-Start can report not run; Bash parks, including reset with cleared heartbeat details. Exceptional Edit keeps its distinct uncertainty mapping.
- [ ] Tool body errors cannot impersonate an executor safe pre claim refusal, including a plain class with the same name. Preserve inner failure details and retained retry limits without swallowing cancellation.
- [ ] Package/policy/engine mismatch or missing claims refuses before engine start/claim creation, becomes a visible executor fault and starts no further segment.
- [ ] Bash crash after effect/before publication yields one marker, intact claims and no model result/continuation on the selected integration.
- [ ] Definitive safe tool errors preserve `is_error`; ambiguous Bash returns no tool result. Recorded old/new histories replay with guarded new Workflow behavior.

## Repeatable file execution

Status: OPEN

Dependencies: [prepared workspace and effect identity](#prepared-workspace-and-effect-identity), [ordered outcomes and refusals](#ordered-outcomes-and-refusals).

- [ ] Repeated Write preserves identical bytes; writes outside `work/`, including `.claude/`, return an error without changing the tree.
- [ ] Atomic temporary write/rename preserves the original on an interrupted write. Edit records pre/post images; retry recognizes post image, applies only from pre image and refuses a third state.
- [ ] Self containing Edit uses one attempt and retains uncertainty after write/before heartbeat; disjoint Edit retry applies once. Record the remaining overlap case explicitly before claiming safety.
- [ ] Reproduce unique match, `replace_all` and read before edit rules only where differential engine evidence establishes them.
- [ ] Adopted native Read/Edit preserves result metadata, errors and file outcome consistency across recovery. Crash after mutation/before publication yields a consistent supported result or blocks recovery; a single prototype file is not general proof.

## Tool behavior fidelity

Status: OPEN

Dependencies: [claimed Bash execution](#claimed-bash-execution), [repeatable file execution](#repeatable-file-execution).

- [ ] Compare engine and selected governed results for Bash/Write/Edit success, errors, missing files, overwrite, unique match, `replace_all` and read before edit rules.
- [ ] Include relative paths and explicitly disposition engine run directory versus effect `work/` differences. Every difference is fixed or accepted with a reason.
- [ ] Run on minimum/newest selected engines or declare the missing lane. Fake model differential tests do not claim real model acceptance.

## Process and payload bounds

Status: OPEN

Dependencies: [claimed Bash execution](#claimed-bash-execution), [prepared workspace and effect identity](#prepared-workspace-and-effect-identity).

- [ ] Distinguish controlled hard stop from graceful cancellation/suspension, inventory surviving owned CLI/tool processes and forbid continuation while ownership or Bash uncertainty is unresolved.
- [ ] Heartbeat all effects, bound silent engine behavior, and distinguish a silent engine from a quiet healthy effect.
- [ ] Preserve cancellation; claimed cancellation waits for in flight completion and reachable process trees end before reporting. Test `setsid` and shell background descendants or name the residual.
- [ ] A 3 MB Write and 5 MB command output stay under the declared history/result caps, with full output stored separately by reference/hash; truncate failure stderr.
- [ ] Explicit graceful shutdown and SIGTERM handling complete/cancel in flight work within configured limits. Capture the uncertain Bash park rather than retrying it.

## Durable waits

Status: OPEN

Dependencies: effect stage exit and gateway/reset/registration decisions in [deployment prerequisites](#deployment-prerequisites).

- [ ] A question survives Worker loss and 30 Continue-As-New handovers, is answered once, and carried state stays within its asserted payload bound.
- [ ] An answer or approval recorded alongside a handover trigger is not lost; a recorded answer wins over same activation timeout, but Workflow cancellation takes priority. Late answers refuse.
- [ ] Absolute deadline expires even before the wake interval; carried wait aging does not cause a handover on every wake. Pending resume actions survive handover.
- [ ] No segment starts against an unanswered pending tool call. Guard new behavior and replay earlier histories.

## Signed decision enforcement

Status: OPEN

Dependencies: gateway decision, [durable waits](#durable-waits).

- [ ] Reject unsigned, forged, expired, cross question, substituted decision, stale version and replayed tokens, including direct frontend Updates and a resume replay after reset.
- [ ] Deterministic verification works in the sandbox; gateway and Workflow canonical JSON digest vectors agree across languages.
- [ ] The registered interceptor rejects unsigned Signals/Updates even with overridden handler bodies. Required validators, aliases and registration cannot silently bypass enforcement. Repeated decisions survive handover and refuse.
- [ ] Replay old unsigned and new signed histories under the selected migration path with historically consistent decisions; guard changed token rules. Document external caller versus trusted Workflow author and gateway flood control.

## Parked run actions

Status: OPEN

Dependencies: [ordered outcomes and refusals](#ordered-outcomes-and-refusals), [signed decision enforcement](#signed-decision-enforcement).

- [ ] Exhausted segment retries, contract, quota, queue and executor faults park with a visible cause. Credential/quota failures do not incur paid retries; transient rate limiting retries only within the declared bound.
- [ ] Signed safe cause retry/checkpoint resume use the correct input/checkpoint; stale park sequence tokens reject. A parked run survives days and handovers.
- [ ] Abort ends with a stated result and cleanup, without authorizing another spawn. Ambiguous Bash never clears claims, returns uncertainty to the model or continues while its safe resolution procedure is unresolved.

## Visibility and registration

Status: OPEN

Dependencies: [durable waits](#durable-waits), namespace registration decision.

- [ ] Start refuses missing required Search Attributes with a stated error before governed execution; normal upserts cause no stalled Workflow Tasks.
- [ ] With live output off, pending decisions remain discoverable by Query and phase visibility; oldest pending time sets and clears correctly.
- [ ] Events include effect key/mode but no raw tool input. Search Attributes contain no tool input/output, workspace paths or question/answer text.

## Reset identity

Status: OPEN

Dependencies: [claimed Bash execution](#claimed-bash-execution), reset procedure and lineage uniqueness decision.

- [ ] Later task reset preserves lineage/run directory; existing claims refuse any repeated or divergent same ordinal Bash and block model continuation.
- [ ] First task reset preserves starter supplied lineage; record actual behavior without a supplied ID and collision handling for concurrent starts.
- [ ] Continue-As-New versus reset is not inferred solely from changed Run Id. Workflow Id reuse obtains a distinct lineage.

## Concurrent and boundary Updates

Status: OPEN

Dependencies: [durable waits](#durable-waits), [signed decision enforcement](#signed-decision-enforcement).

- [ ] Boundary Update is applied in the next run or visibly rejected; record both histories and client result. Two concurrent answers accept exactly one.
- [ ] Repeated decision and client Update IDs refuse after handover. Gateway retry after resource exhaustion is safe and uses the same ID; document Query/retry rules.
- [ ] Decision stage exits only with passing full default tests, replay and explicit contradictions/dispositions.

## Effect isolation

Status: OPEN

Dependencies: decision stage exit, volume/security decision, [process and payload bounds](#process-and-payload-bounds).

- [ ] Effect identity writes only the intended area; cannot write/replace/rename `.claude/` or the run root, read Worker launch environment, or modify claims. Package hashes remain unchanged after hostile attempts.
- [ ] Missing isolation prerequisites refuse rather than launch as Worker identity. Test attempted project allow rules and environment marker exfiltration.
- [ ] No reachable descendant, including `setsid`, survives reported completion; publish exact unsupported process/partition residuals.

## Workspace lifecycle

Status: OPEN

Dependencies: [effect isolation](#effect-isolation), namespace retention decision.

- [ ] Janitor removes eligible closed run directories after grace but never live idle/parked runs, even with old modification times. Unavailable/uncertain Temporal status removes nothing.
- [ ] Namespace and lineage mismatch or Workflow Id reuse never removes another run's files. Retain claims through known retention; unknown retention keeps them.
 - [ ] Missing manifest blocks a segment; explicit reprepare repairs it only while preserving unresolved claims and never recreating them empty. Snapshot before latest prepare lowers generation and parks with no model result; legitimate repair updates generation consistently.
- [ ] State best effort restore detection and the unprotected mid run snapshot rollback boundary. No claims high water guarantee is added.

## Replacement Worker filesystem proof

Status: OPEN

Dependencies: [workspace lifecycle](#workspace-lifecycle), [repeatable file execution](#repeatable-file-execution), selected volume/rig.

- [ ] Remove original local backing disk access and reconstruct accepted transcript, generated files, validated package, manifest/generation, protected claims and outcome from independently retained state. Refuse missing/conflicting state; same host SQLite/snapshot fixtures do not satisfy this check.
- [ ] On two containers, prepared package/hash and generated files are visible across Workers, with consistent numeric ownership. Remove original Worker local disk and restore generated files, package, manifest, claims, session checkpoint and decision/outcome identity independently.
- [ ] Missing/conflicting state refuses continuation; adopted native paths include post mutation/pre publication crashes. Conversation history alone never satisfies file proof.
- [ ] Concurrent exclusive claim creation gives one success and one existing file refusal over stated rounds; the other Worker sees the claim and spawns nothing. Test supported per run serialization semantics.
- [ ] A failed volume test leads to a narrower supported deployment or design change. An unavailable rig stays an explicit untested limit, never a verified cross host guarantee.

## Runtime measurements

Status: OPEN

Dependencies: [effect isolation](#effect-isolation), budget prerequisites for real latency.

- [ ] Measure configured concurrent slot counts, maximum event loop lag, heartbeat timeouts and process leftovers against stated thresholds.
- [ ] Record median/p95 seconds and memory per segment/effect with sample sizes and raw data; derive recommended segment slots from measured peak memory.
- [ ] Record the step cost decision and README limits. A capped run stops and labels partial measurements as partial.

## Deployment versioning

Status: OPEN

Dependencies: workspace stage exit, rollout decision.

- [ ] Prove Pinned task routing, explicit Continue-As-New upgrade to a newer version and rollout of all three queues before migration. Removing compatible effect Workers yields refusal, not silent execution on other code.
- [ ] Rehearse draining only after supported evidence shows no remaining pinned/waiting run. State patching fallback where Worker Versioning is unavailable.
- [ ] Build identity changes with SDK, CLI, hook contract or plugin version. Pin required preview dependencies and document required base/interceptor registration.

## Encrypted payloads

Status: OPEN

Dependencies: [signed decision enforcement](#signed-decision-enforcement), hardening stage entry.

- [ ] Inspect stored history arguments/results for answer, approval and resume Updates with client/Worker codecs; no plaintext marker appears and the valid run still completes.
- [ ] Failure converter hides sensitive stderr markers; Search Attributes remain free of protected fields. Any uncovered payload requires a recorded design change.

## Approval load

Status: OPEN

Dependencies: [visibility and registration](#visibility-and-registration), [concurrent and boundary Updates](#concurrent-and-boundary-updates).

- [ ] During a ten minute segment with more than ten subscribers, approval succeeds or bounded gateway retry succeeds after resource exhaustion; duplicate delivery accepts once.
- [ ] Record Signal batches, history events, Update counts and limit margin. Exhausted retry is a failure requiring a design change, not accepted degraded behavior.

## Session storage conformance

Status: OPEN

Dependencies: session storage decision, [bounded recovery comparison](#bounded-recovery-comparison), [replacement Worker filesystem proof](#replacement-worker-filesystem-proof).

- [ ] With original local backing disk unavailable, recover the exact accepted pending transcript/request from the retained store. Coordinate workspace/claims/outcome checks with replacement Worker filesystem proof; refuse inconsistent state before transport startup.
- [ ] Separate processes with no shared local state read each other's entries; stored bytes contain no plaintext transcript marker and repeated UUID write yields one entry.
- [ ] Dropped/partial writes fail safely without publishing a wrong checkpoint; selected integration restores exact pending calls on replacement without original disk.
- [ ] Missing/mismatched state refuses. Session conformance explicitly excludes filesystem and durable approval/outcome publication, which have their own proving work.

## Patch retirement

Status: OPEN

Dependencies: [durable waits](#durable-waits), [signed decision enforcement](#signed-decision-enforcement), hardening entry.

- [ ] Rehearse patched, then deprecated marker in the same position, then removal only after no replayable run carries it. Replay recent open/closed histories before every deployment.
- [ ] Skipping deprecation produces a failing replay negative control. Earlier released plugin/enforcement and reset histories replay or yield an explicit migration correction.

## Engine promotion

Status: OPEN

Dependencies: [engine compatibility](#engine-compatibility), [deployment versioning](#deployment-versioning).

- [ ] Run newest engine integration/prevention tests daily with an explicit dependency cooldown override and two consecutive results. Broken defer/interception and removed preventive control fail and notify the responsible role.
- [ ] Latest failure blocks promotion; a recorded success permits it. Engine N session resumes on N+1 at Continue-As-New with intact transcript and retained tool results.
- [ ] Apply the adoption criterion map to native/Mods routes; no synthetic route job is reused as proof of another mechanism.

## Shutdown and operational metrics

Status: OPEN

Dependencies: [process and payload bounds](#process-and-payload-bounds), hardening entry.

- [ ] SIGTERM starts graceful shutdown and completion/exit meets Worker/Kubernetes limits; overlong effect cancels its reachable tree, and uncertain Bash parks without repeat.
- [ ] Emit contract violation, unknown outcome and wait age metrics; replay does not increment them again. Record tracing, subscriber/live output bounds and sensitive field exclusions.
- [ ] Measure paid segment retry rate over a stated sample against the target below one percent, or record tuning/failure. Credential/quota fault does not retry; rate limiting stays time bounded.

## Application Workflow acceptance

Status: OPEN

Dependencies: all retained engine/effect/decision/workspace/hardening outcomes, model testing prerequisites.

- [ ] Execute the complete validated skill scenario with resource read, generated file, pending signed decision and claimed Bash in one application Workflow; separate comparison fixtures do not prove this composition.
- [ ] An application authored Workflow with documented registration/policy/security runs the validated unmodified package under its cap, with complete source, configuration, history and credential free run record.
- [ ] Cover resource reading, generated file preservation, a signed effect approval and a human question; record the model's response and pending call/result identity. Native Claude remains the loop, not a replacement custom skill interpreter.
- [ ] Cover two effects in one message, read before/after pause and denial visibility. Every effect is durably recorded; none bypasses the selected governance boundary.
- [ ] Missing required registration/security refuses before any effect. This proves the declared Workflow contract, not arbitrary Workflow compatibility or the later adapter.
- [ ] Cap reached is a safe stop, not pass; any real/fake behavior difference updates design/evidence before completion.

## Evidence and phase reviews

Status: OPEN

Dependencies: each stage's proving artifacts; final review after [application Workflow acceptance](#application-workflow-acceptance).

- [ ] At each exit, update spec/plan/work/evidence with proved, contradicted, superseded, unsupported or unexecuted dispositions. Retained runtime requirements cannot close on source support alone.
- [ ] Record every contradiction's design change before dependent work begins. Dropped keyed service tools, claim release/redo, claims high water and extra contract integer remain out of version 1, not reported as implemented.
- [ ] Account for all retained requirements and technical decisions; inspect every public proving artifact and all partial stage evidence. Missing or declared untested cases settle only through an explicit scope change, never implicit approval.
- [ ] Keep upstream acceptance and harness proof outside core completion. Check public references, complete output, exact revisions and claimed environment coverage without private paths or records.

## Independent final verification

Status: OPEN

Dependencies: [evidence and phase reviews](#evidence-and-phase-reviews), all technical decisions needed for the core outcome.

- [ ] Fix a contract naming artifacts, claims, governing repositories and revisions, exclusions, fresh source identity checks and pass/conditional/fail boundaries. Run complementary fresh contract and adversarial verification.
- [ ] Check deterministic evidence, Temporal design claims, transitive repository changes, actual runtime proving artifacts and all retained recovery/safety requirements. Record unavailable evidence as blocked, not pass.
- [ ] Classify findings; verify proposed remedies before adopting them. Resolve material findings and rerun on revised artifact digests with fresh verification.
- [ ] The final report identifies the exact verified revisions/digests and no unresolved material claim or needed decision. A later design edit invalidates that verdict.

## Upstream submission

Status: OPEN

Dependencies: [independent final verification](#independent-final-verification), collaboration/submission arrangements. Separate from core completion.

- [ ] Follow target conventions and additive API boundaries; verify each reviewed commit with target CI commands and required Python versions, not only branch head.
- [ ] Review all added lines and historical added blobs for confidential/private identifiers before publication. Read CI for the exact pushed revision.
- [ ] Record review request, required contributor license and disposition of requested incompatible API changes. Closing the pull request is rollback; this item grants no commit/push authority.

## Harness effect identity

Status: OPEN

Dependencies: selected core integration; required before [harness adapter](#harness-adapter).

- [ ] State which harness/plugin component mints ordinal, computes key and stores pending identity, with canonicalization and claim semantics preserved.
- [ ] Prove identity stability across retries/handover and change at a new ordinal, or explicitly narrow the adapter guarantee. Keyed service effects remain excluded.
- [ ] Without an agreed identity contract, defer the port rather than inventing ownership.

## Harness adapter

Status: OPEN

Dependencies: upstream landing from [upstream submission](#upstream-submission), [harness effect identity](#harness-effect-identity). Separately verified later integration.

- [ ] A harness example runs a skill through harness approval Updates, with tool start/end events bound to the model call ID and the expected plugin ordering.
- [ ] Denied approval returns a tool error with no effect; claimed Bash Worker loss parks visibly with no next model segment. Exceptional Edit keeps its separate mapping.
- [ ] Prove stable effect identity and question/approval mapping across handover, and document/test whether engine reads emit events or bypass harness policy.
- [ ] Record accepted upstream prerequisites before merging the optional adapter. Rollback removes its import without weakening core safety.
