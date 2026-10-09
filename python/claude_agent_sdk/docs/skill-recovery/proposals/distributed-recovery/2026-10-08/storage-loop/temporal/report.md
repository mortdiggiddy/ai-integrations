# Temporal session ownership and dispatch research (2026-10-08)

Status: research complete, proposed recipe, no runtime qualification. This report supplies corrections and alternatives for the October 8 candidate. It does not adopt a deployment or close an acceptance criterion.

## Direct answers

Yes, Temporal can manage the authoritative accepted conversation and the session's control state. A stable WorkflowId is appropriate for one logical session. The important correction is that a Worker, pod, container or host failure normally resumes the same Workflow Execution by replay on another Worker. It does not require a new RunId. Activity retry changes the Activity attempt. Continue-As-New intentionally creates a fresh RunId under the same WorkflowId and passes the necessary state forward. Workflow retry and reset also create different executions; these are distinct from compute replacement. RunId is an execution identity, not a host identity.

Workflow ID conflict policy controls an already open execution, while reuse policy controls retained closed executions. Reject Duplicate is useful but is not an eternal tombstone: its closed execution protection is bounded by Namespace retention. Terminate Existing is not physical termination of arbitrary subprocesses. Prefer Fail or qualified Use Existing at ingress and application request deduplication. If a session must never be recreated after retention, retain its logical identity/tombstone in an independent durable registry or a qualified long lived entity authority.

The independent dispatch record can use familiar Temporal plus database patterns. Durable Workflow acceptance is a necessary first barrier, but history cannot atomically transact with an arbitrary shell command. Temporal Activity IDs are not downstream deduplication by themselves. Official Activity documentation places idempotency enforcement at the service receiving the operation. Maximum attempts one limits retries of that scheduled Activity, but does not establish completion and cannot protect a manually rescheduled Activity, reset or fresh execution without stable application effect identity.

## Recommended recipe

Recommend one logical session Workflow, a small accepted head and checkpoint receipt in history, immutable exact trajectory blobs in durable object storage using the existing SDK's qualified claim check support where possible, a separately durable workspace, and protected stable effect intent/claims outside workspace rollback. Continue-As-New carries the accepted references, logical lineage, effect ordinal, request deduplication and unresolved ambiguity. The SDK SessionStore is the exact original pending recovery adapter's materialization layer, not necessarily the sole authoritative database for all accepted state. Do not build a second runner or executor.

This is a proposed qualification target. It retains the current controller, host supervisor, observation probe, original pending recovery route, effect Activities after accepted segment commit, one attempt and no fork guard, and ambiguous Bash parking. Existing bounded Phase 1 results remain evidence for their specific routes only. Worker/host loss is in scope; Temporal Service disaster recovery, regional loss and forced Namespace failover require a separately chosen failure contract and are not assumed here.

### Conversation authority alternatives

| Alternative | Sanctioned building blocks | Qualification gap | Recommendation |
|---|---|---|---|
| Exact bounded transcript deltas returned as Activity outputs, reconstructed by Workflow state | Activity completion payloads in history, deterministic replay, Query reads, Continue-As-New | Exact Claude opaque entries, UUID conflict checks and original pending recovery adapter remain to prove; full trajectory handover can exceed limits | Valid bounded comparison lane |
| Small accepted head in history and exact immutable trajectory chunks in object storage | Claim check / External Storage, SDK Payload Converter and Codec, immutable object identities | Blob durability, retention, integrity, missing reference refusal and SDK adapter compatibility remain to prove | Recommended scalable lane |
| Transactional shared SessionStore as primary transcript authority, head references in Workflow | Conditional append and existing SDK contract | Database acknowledgement, lost acknowledgement, concurrent heads and rollback behavior remain to prove | Preserve as a qualified alternative, not mandatory topology |

Do not describe a Query as storing the conversation. Queries read existing Workflow state and are not history events. The state must have entered history through accepted messages, Workflow input or accepted Activity outputs. A Query returning a full reconstructed trajectory can add no history events while still increasing transport payload and replay/memory pressure. Reading an external store from Workflow code or Query is not permitted; access is through Activities or the configured data conversion mechanism.

The built in External Storage feature is Public Preview. It externalizes encoded payload bytes and passes references through history; it does not provide distributed filesystem snapshots, cross store transactions or host fencing. The official driver/library is prior art worth qualifying before authoring a new blob implementation. This research authorizes neither installation nor an SDK upgrade. Current installed/pinned source compatibility remains a test gate.

Small delta persistence avoids repeatedly inserting the complete trajectory into every Activity input and output. Every chunk binds its exact bytes, native entry ordering and UUIDs, original pending tool identity/result, accepted parent head and checkpoint versions. Workflow acceptance must reject a conflicting UUID, stale parent or mismatched workspace receipt. A write acknowledged by object storage before Temporal Activity completion is an unaccepted candidate until history accepts it. Missing or corrupted accepted data refuses recovery; a friendly summary or fresh session is not a substitute.

Continue-As-New cannot mean dropping the old accepted transcript or assuming expired earlier run histories will always be readable. Pass/reanchor a bounded head whose immutable blobs remain retained throughout all supported recovery windows. Object lifecycle must account for live references, indefinite session chains, reset windows and legal retention. The simple TTL formula in the external storage docs is not sufficient if a new run merely retains references to older objects without rewriting or renewing them.

### Dispatch and exactly once business effects

The validated common pattern is a stable application idempotency key passed to the receiving system, which records the key and business mutation atomically, then returns a recorded result for duplicates. A SQL uniqueness constraint plus mutation in the same database transaction is a concrete reference. A transactional outbox similarly commits the intent together with a local database change; its delivery can still repeat and therefore needs an idempotent receiver. Saga compensation is recovery for supported business operations, not proof that a shell command never repeated.

The common example RunId plus ActivityId key is stable across retries within one run. For this product, effect identity must instead be tied to the logical session lineage and original accepted call/ordinal and input digest, because Continue-As-New, reset or a new execution changes RunId. Preserve input binding so accidentally reusing an identity for a different command refuses.

For arbitrary Bash, a protected intent/claim before spawn can conservatively prohibit redispatch. A crash between recording intent and executing leaves uncertainty: the command may have run or may not have run. A crash after the command succeeds but before outcome persistence has the same uncertainty. This is not an exactly once completion promise. Record and park the ambiguous operation for reconciliation. Never restore an old workspace and infer that no command ran because its local marker disappeared. Never mint a new ordinal or lineage to escape the old intent.

A separate entity Workflow can serialize claims independently of workspace snapshots and of a session reset. It is a testable alternative to a transactional database, not a demonstrated implementation here. Its own reset/retention/backup restore controls, lookup on recovery, duplicate request semantics and capacity must be qualified. In that alternative, the ledger owns effect Activity scheduling with one attempt; duplicate requests return status or a recorded result rather than replayable permission for the caller to spawn. Continue-As-New retains the claims. Reset/recreation of the ledger is forbidden or separately governed under the selected failure contract. A claim Workflow acceptance is still not atomic with external spawn and does not kill a stale host. No consumer can gain dispatch authority merely by discovering a lease or a Workflow query result.

## Actual harness prior art

The public repository resolves to temporal-community/temporal-agent-harness, inspected at f50412138cab078f19c54e683e7ba5e529323f17. Its README states the project is early and experimental. SessionManagerWorkflow.create_session checks an explicitly supplied session_id against its remembered sessions, starts a child Workflow with that ID and returns the previously tracked session for redelivery. This is concrete session ingress/idempotent creation prior art. It is not eternal identity protection or a physical single execution guarantee. Its retained list also needs lifecycle qualification for this product.

The harness has typed message handlers, validated Updates, observable committed state, and Activity sandbox delegation in its OpenAI integration. These are useful outer harness references. README line 576 explicitly distinguishes replay of the filesystem tree from current contents of its backing store. This rejects the assumption that a durable agent event stream automatically snapshots all external filesystem state. A source read of its OpenAI sandbox wrapper establishes Activity routing, not support for our mandatory Claude SDK original pending recovery path.

Atlas found a replay aligned transcript example that mints message IDs in deterministic Workflow code and retries a model Activity using the same ID. It is useful reference prior art, not a sanctioned Claude integration or proof across reset. The Atlas current harness source directory was unavailable at the queried code path; public pinned source supplied the actual harness read instead. The earlier temporal-agent-harness-example URL returned 404. Do not claim an actual map or runtime test of that older repository.

## Current issue 31 disposition

The GitHub public comments API returned 11 comments through 6043344791. Comment 5939515083 proposes conversation state in the Workflow and Query readback, with SessionStore optional. Comment 6026506600 lists filesystem failover and repeat Bash/MCP effects as unresolved. Comment 6032736083 proposes checkpoint cwd snapshots or shared disk and a single attempt plus uncertain outcome policy; it does not demonstrate distributed snapshots or physical host fencing. Its callback reproduction is SDK 0.2.154 / CLI 2.1.274 without policy. Comment 6040777162 distinguishes that result injection failure from original pending recovery on SDK 0.2.162 / CLI 2.1.274. Neither generalizes across resume paths or storage topologies. The remaining comments through 6043344791 add permission to port a prototype, corrected links and progress context, not new durability proof.

## Proposed corrections and tests

1. Replace the mandatory primary transactional SessionStore formulation with a trajectory authority contract supporting the three qualified alternatives above. Preserve exact original pending recovery and conditional conflict refusal; qualify actual immutable blob plus SDK adapter behavior before selecting it.
2. State compute replacement keeps WorkflowId and ordinarily RunId. Treat container identity, host identity, Activity attempt, engine session identity and Continue-As-New RunId as different identities.
3. Record closed WorkflowId uniqueness as retention bounded, and keep application identity and effect keys stable across all permitted execution chain/reset operations.
4. Require tests that kill a Worker before/after accepted Activity completion and observe same RunId, exact accepted head reconstruction and zero native effect duplication. Pending selected recovery segments still refuse automatic retry rather than silently admitting attempt two.
5. Require tests for query readback of accepted exact transcript, conflicting entry UUID, stale parent, lost object acknowledgement, accepted blob missing/corrupt and mismatched workspace receipt. Measure actual serialized payloads/history, not nominal strings.
6. Require Continue-As-New under concurrent Updates, exact state handover and no dropped accepted message or duplicated original result. Verify no old referenced object expires while a live new run still needs it.
7. Require effect server duplicate tests with same key/input and conflict tests for same key/different input; reset and fresh run replay must use the same logical key. Physically count effects. Workflow history completion counts alone are not the oracle.
8. Require Bash intent written before spawn and failure injection around every intent/claim/spawn/outcome/Activity completion boundary. A restored preintent workspace must not enable redispatch. Unknown outcomes park even with maximum_attempts=1.
9. Require partition tests where the old Activity keeps running after timeout. The new Worker cannot dispatch until independent termination or effective fencing proof is obtained. Heartbeat/cancel/notfound are progress signals, not physical termination receipts.

## Sources and actual tool use

Five successful calls to the discovered Temporal Docs connector are captured, public primary sources only, in primary-docs.json. Three successful Atlas queries searched session IDs, the actual harness and replay aligned transcript. Two Atlas read calls: actual harness directory lookup failed; replay aligned source read succeeded. Installed spec-driven-temporal SKILL and relevant README constitution, temporal:temporal-developer SKILL, core patterns/gotchas and Python external storage guidance were read directly. No native Claude Skill invocation is claimed.

Public reads: one web.open call with two URLs (issue31 body successful, older example repository404); GitHub issue comments API read; GitHub metadata/commit/tree reads for both harness repository aliases; seven distinct pinned source files read over raw GitHub, with SessionManager read twice for exact lines. Captured hashes are in harness-source-excerpts.json. None of these are execution or test evidence.

Decisive primary URLs:

- https://docs.temporal.io/workflow-execution/workflowid-runid#workflow-id-reuse-policy
- https://docs.temporal.io/workflow-execution/continue-as-new
- https://docs.temporal.io/best-practices/worker#manage-event-history-growth
- https://docs.temporal.io/activity-definition#idempotency
- https://temporal.io/blog/idempotency-and-durable-execution#idempotency-keys
- https://docs.temporal.io/evaluate/features/workflow-message-passing
- https://docs.temporal.io/external-storage
- https://docs.temporal.io/external-storage#choose-storage
- https://docs.temporal.io/external-storage#lifecycle
- https://docs.temporal.io/design-patterns/fixed-wall-time-retries
- https://github.com/temporal-community/temporal-agent-harness/blob/f50412138cab078f19c54e683e7ba5e529323f17/temporal_agent_harness/web/session_manager.py
- https://github.com/temporal-community/temporal-agent-harness/blob/f50412138cab078f19c54e683e7ba5e529323f17/README.md
- https://github.com/temporalio/ai-integrations/issues/31#issuecomment-6032736083
- https://github.com/temporalio/ai-integrations/issues/31#issuecomment-6040777162

The official blog's conceptual SQL pattern is referenced; its incidental Python pseudo API is not implementation guidance. No claim relies on a retrieved statement that zero retry attempts means no retries. The existing explicit maximum_attempts=1 guard remains unchanged.
