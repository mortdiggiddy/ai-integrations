# Independent Temporal and complete Issue 31 sweep

Date: 2026-10-08. Author scope: research only. Verdict: the discussion has reusable solutions and bounded project demonstrations, but the complete requested outcome is not demonstrated. This report inspected the issue body and all 12 captured comments, including 6026506600 and 6065563646, the four current candidate files, the existing ownership audit and relevant private ticket sections. It did not read the other new research agent's report before reaching these findings. No source, ticket, runtime, dependency or accepted contract was changed.

The operator's requirement that EVERYTHING be addressed changes coverage expectations. A documented exclusion can explain current behavior, but cannot count as delivery of a requested capability. Existing bounded DONE dispositions remain valid. The later durable child and parallel execution extension needs prospective owned work and adoption gates rather than reopening DSR-1.5 or treating its child denial as medium priority completion.

## Direct answer about storage

There is a real supported SDK mechanism for externalizing payload bytes. There is a proposed application recipe for exact accepted Claude trajectory, workspace and independent effect authority. There is not yet a demonstrated complete deployed storage solution for this product's host loss and uncertainty contract. These are three different answers.

Temporal's current [External Storage overview](https://docs.temporal.io/external-storage) marks the feature Public Preview. It replaces large payloads with reference claims, runs after the codec, and has a default 256 KiB threshold. Storage must remain durable, reachable and consistent for all consumers. Temporal does not automatically delete stored payloads; failed requests can leave orphans. Driver failure fails a Task attempt and the Task may retry. Cross region replication can temporarily miss newly written data. These are payload lifecycle and availability responsibilities, not filesystem checkpoint or exclusive process ownership guarantees.

The [Python guide](https://docs.temporal.io/develop/python/data-handling/external-storage) provides the actual DataConverter integration and first party S3 driver using the aioboto3 extra, configured wherever Clients and Workers encode or decode data. Custom drivers are possible. The [Python SDK 1.25.0 release](https://github.com/temporalio/sdk-python/releases/tag/1.25.0) introduced External Storage and the S3 driver as prerelease features. The retained integration uv.lock currently selects temporalio 1.33.0. That exceeds the introduction version, but neither that lock nor the issue's upstream large result benchmark proves installed driver availability, backend configuration, lifecycle controls or this product's actual lane compatibility. No installation or credentials inspection occurred.

Recommended comparison target, still awaiting BD-6 and owner decisions: Temporal stores accepted orchestration and bounded immutable references; the existing SDK adapter materializes exact opaque conversation bytes; independently durable object storage holds trajectory chunks and sealed workspace bundles; separately retained dispatch authority and existing protected spawn admission prevent replayed unknown effects. A transactional SessionStore and qualified shared filesystem are comparison alternatives. No new executor is necessary. Storage selection remains DSR-0.6/DSR-0.11; conformance DSR-5.4; physical cross host proof DSR-4.3. Object storage alone does not expose the native POSIX workspace the Claude engine needs.

## Important additional failure case

Inference from documented Task retry behavior: an external effect can succeed inside an Activity, then its large result upload or Activity completion can fail. Ordinary Activity retry may repeat the effect even though the driver, not the effect, failed. Add a fault immediately after a physical counter increments and before result publication; assert no second effect, preserve exact known outcome if independently recorded, otherwise park with no next model segment. Also fail input retrieval before effect start, completion acknowledgement after successful upload, and restore of an older object/claim. These are proposed qualification tests, not observed product defects. Owners: DSR-2.3/DSR-2.7, with DSR-5.4 storage injection and DSR-3.5 reset coverage.

Continue-As-New must preserve referenced old objects or explicitly reanchor them. A new Run that merely carries an old immutable reference cannot assume that the old Run's expiration permits deletion. The candidate already states this stricter live/reset horizon. Do not adopt a finite TTL for an indefinite business session without demonstrated reference lifecycle handling.

## Complete discussion outcome ledger

Source: [issue body and complete discussion](https://github.com/temporalio/ai-integrations/issues/31), preserved locally in [capture](../provenance.md#p-035). The captured record count is 13 including the body; the outcome grouping below is this report's interpretation, not an acceptance count. Every historical comment has a disposition in the existing [reviewer ledger](../provenance.md#p-043).

| Requested or discussed outcome | Current result and owner | Observable remaining proof |
|---|---|---|
| High: restart and builtin Activity latency | DSR-4.4 owns measurements; cold/warm/hybrid remain comparisons, not selected implemented optimization. | Real model and stand in latency distributions, engine start counts, queue/load configuration and cold fallback after loss/reset; separately select optimization scope if targets fail. |
| High: repeated Bash/MCP effects | DSR-2.2/2.3 proposed independent intent and mandatory park. Local original result recovery is bounded evidence, not arbitrary idempotency. | Counter across effect success/result loss, retry, timeout, worker loss, outer Reset, ledger reset refusal and duplicate request; preserve original MCP tool use ID, and prove receiver dedup separately if claimed. |
| High: Edit/Write metadata bug 99041 | DSR-2.4/2.6; bounded native result replay exists as prior art; latest port only attributed until public revision pinned. | Exact original native result records, Read then Edit, Write to a read file, hidden metadata and restored pre/postimages across replacement. |
| High: filesystem follows failover | DSR-0.6/4.1/4.3; immutable bundle and reattachment proposals. | Destroy old host after accepted checkpoint; restore exact files/deletions/links/modes/native metadata elsewhere; publication gap and rollback negatives; no old writer surviving. |
| High: launcher/lock failure | DSR-2.7/4.1; public fail closed default proposal distinct from host fencing. | Inject launcher and lock failure before effect and observe zero effects; descendant survival and lost cleanup reply must prevent replacement. Explicit opt out cannot inherit default guarantee. |
| Medium: durable subagent tools | No active delivery owner currently. DSR-1.5 intentionally denies unsupported children. Proposed DSR-7.4 below. | Active child pending state, approval/result identity, child tree cleanup and replacement, missing child state refusal. |
| Medium: parallel builtin tools | DSR-2.6 comparison does not deliver batch support. Proposed DSR-7.5 below. | Multiple real calls each get their own Activity/result exactly once; partial completion and conflicting filesystem updates cannot silently repeat or corrupt state. |
| Low: policy API | Bounded DSR-1.2 proof; DSR-7.1 prospective upstream mapping to existing options. | One code path preserves policy default behavior, tool_activities, tool_approvals, timeout/retry options and exact allowed/denied effects under supported routes. |
| Low: questions | DSR-1.6 bounded DONE; DSR-0.7/3.2/3.6 production signed decisions and gateway remain OPEN. | Original call committed before answer, typed exact JSON, authenticated stale/duplicate/racing answers and cancellation/handover behavior. |
| Workflow owned conversation, Query, optional SessionStore | DSR-0.11/5.4; candidate has alternatives. Query reads existing state rather than persisting it. | Exact accepted prefix and conditional append, conflicting writer rejection, reconstruction on another host, incompatible schema/version refusal. |
| 10,000 calls and Continue-As-New | Upstream body reports finite benchmark; DSR-3.1/3.6 production governed handover remains pending. | Retained identity/claims/answer dedup across handover and reset, handler drain and bounded serialized state; reuse benchmark fixtures with matched provenance. |
| 40 large results and External Storage | Upstream body reports 40 one MB results with 84 KB history; DSR-2.7/5.4 owns product proof. | Pin driver/runtime/backend; retrieve every exact result after replacement, inject upload failure after effect, prove lifecycle through live/reset/replay and inspect actual history growth. |
| Live Workflow Streams | DSR-5.3; prior body reports text/tool/approval/retry continuity. | Subscriber reconnect/dedup/order across handover, no stream event promoted to accepted trajectory before commit, explicit loss semantics and load limits. |
| Replay, golden histories, cancellation/reset/timeouts | DSR-5.5/3.5/2.6; upstream credential free real engine/stand in corpus is reusable prior art. | Replay selected unchanged histories, schema/command drift negatives, cancellation before/after effect and exact externally witnessed outcomes. Replay alone does not prove physical filesystem restoration. |
| SDK floor/newest/platform/permission mode | DSR-5.6 and retained bounded DSR-1.7; reported missing Windows wheels and auto mode matter. | Platform package provenance and actual engine startup; explicit permission mode; current release upgrade resume. Do not raise floor to solve unavailable binary. |
| Synthetic resume input closure | Preserve synthetic route DEFECT, selected original pending PASS and new bounded replay route as distinct. DSR-2.6/5.6 owns future comparison. | Per route hook/callback counts, allowed and denied Bash physical witnesses, ask/deny/suppression/missing answer; no callback execution cannot be scored as callback enforcement. |
| Transcript bug 97358 and resume bug 97196 | Linked issues and upstream avoidance are captured, not new universal fixes. DSR-2.6 owns regression comparison. | User row after pending call, several results with original IDs, cancellation/turn boundary exact transcript; selected supported route either passes or explicitly refuses before effects. |
| Separate task queues | Source says not exposed yet; candidate proposes distinct segment/effect roles. DSR-2.7/4.1 owns wiring and confinement. | Workflow/segment/effect/supervisor tasks reach selected queues; misplaced or privileged effect worker refuses and no credentials leak. |
| Package validation/signing/Mods | DSR-1.5 bounded DONE; DSR-3.2/4.1 production qualification. Optional Mods need BD-6 selection. | Exact package/session policy across resume and reload; no plugin or native capability escapes independent prevention. Mods store is not trajectory authority. |
| Repository placement, acceptance, contributors, corrected links | Historical DSR-0.5 DONE and cancelled Slack remain. DSR-7.1/7.2 own prospective submission/adapter. | Record suggested versus accepted upstream scope and source credit; external review only on explicit contact/publication authorization. Historical fixes only statement is superseded; newest local port is not yet inspected PR source. |

The [latest comment](https://github.com/temporalio/ai-integrations/issues/31#issuecomment-6065563646) materially separates bounded tool replay from resumed segment callbacks. It reports a hook only executor, no callback invocation, ask refusal and deny tool omission. Its source revision was not published in the inspected PR head. Future comparison must not drop scoped ask controls merely to run this alternative or call absent permission stream a repair of the synthetic resumed segment route.

## Proposed prospective DSR-7.4: qualify durable child tools

Status recommendation: OPEN, prospective extension awaiting BD-6 adoption. No estimate or delivery approval is asserted. It is not a reopening of DSR-1.5. Related: DSR-2.6, DSR-3.2/3.6, DSR-4.1/4.3, DSR-7.2/7.3. Dependencies: explicit expanded recovery contract and selected source/runtime; complete parent recovery/containment/storage prerequisites; separate runtime approval for actual experiments. If upstream release provides child APIs, reuse them instead of authoring a second executor.

Proposed acceptance criteria:

- Identify every admitted child, parent, original pending tool and exact trajectory/workspace receipt; unsupported or partially captured children still refuse before startup.
- Demonstrate an actual child durable effect Activity and exact original child result delivery, with no substitute main agent result or copied text summary.
- Preserve parent/child logical effect identity across retries, replacement, Continue-As-New and supported Reset; duplicate completion or Update cannot schedule another effect.
- Route child approval/question through the same governed authentication, policy and uncertainty rules; denied request has zero physically witnessed effects.
- Kill parent process, child process, container and host at distinct before/after effect windows; recover only qualified state after authoritative whole tree cleanup. A child surviving parent exit prevents replacement.
- Preserve concurrent independent child isolation and explicitly serialize or reject shared workspace conflict; child writes cannot mutate parent package, conversation authority, claims or supervisor state.
- Mixed supported/unsupported child tree, forged parent ID, missing child state and callback/hook suppression refuse or park without model continuation.
- Record exact source/API/platform limitations and demonstrate the existing serial parent path still behaves identically when extension disabled. No deployment claims until all applicable criteria have evidence.

The experimental [SDK recovery README](https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/README.md#main-agent-recovery-with-a-session-store) explicitly bounds its recovery to the main agent. The maintainer's [priority comment](https://github.com/temporalio/ai-integrations/issues/31#issuecomment-6026506600) points to only a partial child prototype. These are real capability constraints to resolve, not reasons to label the requested child outcome complete.

## Proposed prospective DSR-7.5: qualify parallel native tool batches

Status recommendation: OPEN, prospective extension awaiting BD-6 adoption. No estimate or delivery approval is asserted. Related: DSR-2.4/2.6/2.7, DSR-3.2/3.6, DSR-4.1/4.3 and DSR-7.4. Dependencies: exact native call/result fidelity, adopted batch ordering/conflict contract, stable authority and complete containment; separate runtime approval.

Proposed acceptance criteria:

- Real engine emits at least two builtin calls in one message; each admitted call has exact original ID/name/input and separately recorded Activity/authority identity.
- Preserve all original results and native Write/Edit metadata in the exact accepted trajectory; an extra user row, duplicate or reordered result cannot drop another result or fabricate success.
- One call finishes, another fails or parks, and replacement recovers known outcomes without rerunning completed or ambiguous effects. Explicitly define whether parent continuation waits for all results or parks the whole batch.
- Conflicting Edit/Write preimages, overlapping paths, deletes and shared hidden state serialize or refuse under a documented rule. Parallel scheduling is not assumed filesystem commutativity.
- Approval, denial, stale answers and cancellation apply per original call; denied calls have zero effects and accepted siblings follow the selected atomicity contract.
- Duplicate scheduling, Activity result upload failure, Worker/container/host loss and supported Reset preserve exactly one admission per stable effect identity; ledger rollback never clears uncertainty.
- Whole descendant cleanup and exact workspace receipt prove replacement exclusivity even with several active tool processes. Missing captured result or batch member prevents unsafe continuation.
- Define finite batch size, storage/history/capacity limits and measure performance against serial baseline; existing one call mode remains unchanged when extension disabled.

The source reports both initial solo defer limits and later partial multiple result handling. Parent or batch orchestration can reuse Temporal Activities, but their completed results do not make native shared workspace updates independent. The exact acceptance protocol above is proposed application work, not a sanctioned complete recipe found in Docs.

## Temporal precedent and authority limits

The [Entity Workflow pattern](https://docs.temporal.io/design-patterns/entity-workflow) supports long lived identity and message driven state with handler drained Continue-As-New. Update deduplication is per Run, so the application carries retained dedup state across handover. A separate dispatch Entity Workflow is a plausible independently retained scheduling authority, not an automatically reset proof service. Its admin Reset, terminate/recreate, retention and forgotten keys need the candidate's explicit controls and fault tests.

[Activity idempotency guidance](https://docs.temporal.io/activity-definition#idempotency) supports receiver enforced idempotency and stable business operation identity. An Activity ID or maximum_attempts=1 alone does not make arbitrary Bash exactly once or resolve an effect with lost outcome. A duplicate reply must report status rather than a reusable spawn permit; unknown physical outcomes remain parked. Host failover usually replays the same Run, while Continue-As-New creates a new Run, so Run ID is unsuitable as the sole logical effect identity across supported operations.

The complete recipe is a composition with partial precedent, not a claim of novelty. Existing native replay, experimental exact recovery, optional store, upstream golden corpus, Temporal entity and storage primitives should be reused where compatible. No matching complete product implementation was found in this bounded sweep. That is an evidence limit, not proof of first invention or absence elsewhere.

## Comparison after independent reports

After this report was written, this agent read [the independent industry report](agent-industry.md). Both independently conclude that all nine priorities are not yet delivered, durable child and parallel execution require positive prospective work, and the external storage recipe is viable but unqualified. Both separate the same four permission routes and reject treating the new no callback toolstep as inherited callback proof.

The reports contribute different fault vectors. The industry report adds documented Docker sandbox exit persistence and concurrent overwrite, refused E2B pause leaving execution alive, and Daytona mount nontransactionality. This report adds externalized result upload failure after a successful physical effect. All belong in selected backend/containment qualification, not runtime PASS claims. Current DSR-4.3's shared volume scope excludes object/microVM strategies; adoption must explicitly update prospective scope before such a strategy can satisfy it.

## Tool and execution record

Two successful Temporal Docs connector calls were made after discovery in this agent's runtime. Queries covered External Storage maturity/drivers/lifecycle and Update/Continue-As-New/reset/idempotency. One completed Atlas wrapper query, `external storage storage driver payload lifecycle session store`, returned SDK external storage PRs and no exact keyword match; a preceding longer wrapper query was also issued. Public primary Docs, Python release and issue pages were read with the web tool. Local captured issue text supplied all comment bodies. Installed source was not imported, no dependency changed and no model or infrastructure experiment ran. A first local read command used unavailable `python`; it was rerun successfully with installed `python3` without installing anything.

Only this new report was authored. Existing ticket statuses, candidate files, source captures, frozen snapshots and raw archives remain unchanged by this agent.
