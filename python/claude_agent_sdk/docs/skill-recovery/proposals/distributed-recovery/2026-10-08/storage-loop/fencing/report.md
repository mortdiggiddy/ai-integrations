# Dispatch and termination research (2026-10-08)

Status: COMPLETE research; candidate recipes remain unimplemented and unqualified. No runtime, model, installation, provisioning or contact occurred.

## Answer

Temporal machinery can own dispatch intent and accepted outcomes outside workspace rollback. A separate SQL database is an option, not an intrinsic requirement. A retained, independently protected Entity Workflow is a plausible competing authority. Standard Temporal Activities, Entity Workflows, Update deduplication, bounded retries and downstream idempotency are documented components. Their composition with exact original Claude pending recovery and physical fencing is not yet validated in this project.

Workflow identity controls orchestration admission, not the number of living operating system processes. Worker or pod replacement ordinarily reconstructs the same Workflow Run from history; it does not need a new Run ID. Continue-As-New, Workflow Retry and Reset create new Runs for separate purposes. Logical session and effect keys must survive those changes. Reject Duplicate applies only within retained closed history; it is not a permanent never-start-again registry. Source: https://docs.temporal.io/workflow-execution/workflowid-runid

## Current reality inspected

The existing `_workflow.py:615-654` adopts the segment checkpoint and original deferred call before `_run_tool`. Its policy path at `_workflow.py:699-719` still raises `PolicyExecutorUnavailable`; the proposed production policy executor is not installed. The generic tool path schedules regular Activities with configured retries and Activity ID `tool-{call.id}`. Its remembered recent IDs are not a permanent independent dispatch ledger.

The selected original pending runner at `_runner.py:682-685` rejects attempt other than one or fork. Controlled skill admission at `_runner.py:1282-1285` keeps project loading and `plugins=[]`. These guards remain mandatory. The proposed recipes cannot quietly use an automatic segment retry or a new Run ID to bypass them.

`write_recovery.py:199-241` creates an exclusive invocation file before the fixed Bash command and parks ambiguous outcomes. This is a retained fixture, not distributed rollback protection. `host_session.py:381-437` verifies resource/label/name identity, Docker wait, Running false, PID zero, removal and absence, and keeps admission refused on uncertain cleanup. Its docstring explicitly requires the same local daemon. It is local containment evidence, not a two-host termination guarantee.

The inherited October 7 agent-C report already proposed independent intent, protected claims, provider or physical fencing, and two-host partition qualification. This pass sharpens the authority alternatives rather than invalidating those requirements.

## Common validated patterns and their boundary

| Pattern | Precedent | Fit and limitation |
| --- | --- | --- |
| Regular Activity completion recorded in history | Sanctioned Temporal mechanism | Restores known recorded outcome on Workflow replay; not an atomic transaction with arbitrary external effects. |
| Stable downstream idempotency key | Sanctioned vendor pattern and SQL example | Retries safely only when the effect system enforces key uniqueness atomically with its own mutation/result. |
| Entity Workflow state via Signals/Updates | Sanctioned pattern | Durable ordered logical intent, bounded state handover and deduplication. Does not kill a stale container. |
| maximum_attempts=1 | Sanctioned bounded retry pattern | Avoids automatic repeat of a nonrepeatable Activity. Crash after effect but before completion leaves outcome unknown. |
| Async Activity completion / Signal callback / polling | Sanctioned external completion choices | Retrieves definitive external outcomes if the provider has stable operation identity and reliable query/callback. Does not invent missing results. |
| Local Docker stop/wait/PID-zero/removal | Existing bounded project evidence | Reuse on qualified same-daemon lane. Does not prove old host death during partition. |
| cgroup.kill plus populated=0 | Linux mechanism, partial composition | Kills and observes contained descendants on reachable trusted host. Requires containment/escape tests and stable cgroup identity. |
| Kubernetes out-of-service handling | Sanctioned administrative mechanism, partial composition | Requires node already shut down or powered off; it does not itself establish that fact. |
| Arbitrary Bash exactly once after unknown outcome | none_found within this search | Independent intent can enforce never redispatch; it cannot recover unknown stdout/exit/effects or ensure operation completion. |

Official Temporal idempotency article demonstrates operation-key insertion and mutation in the same SQL transaction. Placing a receipt in one database and making an arbitrary HTTP call is a different two-system protocol. An outbox helps retain dispatch work, but consumers still need downstream idempotency or a reconciliation contract. Source: https://temporal.io/blog/idempotency-and-durable-execution

For ordinary Activity retry within one Run, Workflow Run ID plus Activity ID is the official example key. For this product's recovery across Continue-As-New/Reset/restart, use a separate immutable logical session lineage plus original call ordinal/key and input digest. Never include Activity attempt or current Run ID in that cross-run identity. This extends the example; it is an application requirement, not a platform-generated key promise.

Temporal Activities may time out while code continues. Cancellation is cooperative, received through heartbeats and may be ignored. Default retries therefore must not substitute for termination or idempotency. Source: https://docs.temporal.io/activity-execution

The official fixed-count pattern explicitly permits maximum_attempts=1 for nonidempotent calls, acknowledging the effect-success/result-loss window. This supports conservative parking. Source: https://docs.temporal.io/design-patterns/fixed-count-retries

## Competing authority recipes

### T: Temporal-owned intent and single scheduling decision

Use a long-lived Entity Workflow keyed by immutable namespace and logical session lineage, outside the resettable outer session Workflow. It records original effect key, digest, accepted checkpoint reference, owner identity, status and exact outcome reference. A synchronous nonblocking handler atomically rejects conflicting keys and queues a first intent. The main loop schedules the existing trusted effect Activity once with maximum_attempts=1; it never reschedules an ambiguous operation. Outcome retrieval and harmless reconciliation Activities can retry separately.

Only an independently verified accepted segment receipt may enter the effect queue. A caller's assertion that a segment completed is insufficient. The bridge must validate receipt identity/history/state before launching through the existing wrapper. No native shell or direct Mod dispatch bypass is authorized.

Duplicate requests return status or exact known result, not another execution opportunity. A particularly dangerous variant returns "permission granted" from an Update and lets each caller spawn Bash: a retried Update can return the original successful result again. A completed Update is durable state evidence, not a consumed one-shot spawn capability. Having the Entity Workflow own the one scheduling decision avoids that specific replayed-permit design. Retain the independent wrapper guard until the composition is qualified.

The authority must not be reset, restarted fresh, deleted, expired or restored to an earlier state while any relevant effect can still be replayed. Outer Reset consults this independent authority. Continue-As-New carries all outstanding claims/tombstones/dedup keys and waits for handlers. Server Update-ID dedup is per Run, so application dedup persists across handover. Authority missing or regressed means refuse, never recreate automatically. Source: https://docs.temporal.io/handling-messages

A separately started Entity Workflow is the simplest lifecycle separation. A child Entity Workflow is possible only with deliberate ParentClosePolicy=ABANDON, confirmed child start before parent exit, stable logical ID, compatible recovery lookup and administrative protection from resetting/deleting it. ABANDON prevents parent close propagation, not administrator deletion, retention loss, or external side effects. Source: https://docs.temporal.io/parent-close-policy

This option reduces separate database operations but introduces authority-Workflow lifecycle, update routing, admission verification, bounded history and operator policy obligations. It does not eliminate workspace storage or physical fencing. Source for sanctioned entity pattern: https://docs.temporal.io/design-patterns/entity-workflow

### S: SQL or equivalent protected independent authority

Atomically insert a unique intent key and digest into a store outside workspace snapshot restore. States and immutable outcome references are monotonic. Conflicting duplicate key refuses; existing uncertain key parks; exact known result can be reconciled. A separate invocation guard prevents repeated local spawn. The store needs tested durability, concurrency, restore policy, authorization and retained lifetime. Unique insert before shell is deliberately conservative: a crash before spawn can leave a permanently parked operation.

If the mutation belongs to the same database, one transaction may include key, mutation and result, matching sanctioned idempotency. If the mutation belongs to a provider, use its own enforced idempotency key and queryable result. For arbitrary Bash or tools without such a contract, there is no transaction spanning database intent and shell exec. The no-redispatch recipe preserves safety at a cost of availability.

Neither T nor S is adopted here. Both are testable; BD-2/BD-3/BD-6 must select exact authority and retention/reset scope. Temporal T is not disqualified merely because no SQL ledger exists.

## Why leases and storage are not termination

An ownership epoch or CAS record can serialize new admissions but stale code continues unless every actual write/effect destination rejects its stale token. A revoked storage writer may still call an external API. A lease expiring or a Temporal Activity timing out is not evidence that the old environment stopped. A gateway or effect broker can enforce epoch checks at the destination, but it works only if every capability is mediated and in-flight requests are accounted for. Direct arbitrary Bash/network credentials defeat that coverage. This is a bounded capability option; it preserves the existing SDK runner and wrapper instead of adding another general executor.

Kubernetes force deletion immediately frees the API name without confirming kubelet termination and can create a replacement alongside a still-running Pod. Source: https://kubernetes.io/docs/tasks/run-application/force-delete-stateful-set-pod/

Volume access modes do not enforce write protection on a mounted volume. RWO and apparent VolumeAttachment deletion are not general stale-writer fencing. Source: https://kubernetes.io/docs/concepts/storage/persistent-volumes/

For non-graceful recovery, Kubernetes requires verification that a node is already shut down or powered off before out-of-service taint. Its forced detach timeout can leave still-running workloads and cause corruption. Use provider/BMC confirmed power-off or a separately qualified runtime terminal receipt; park while that authority is unreachable. Source: https://kubernetes.io/docs/concepts/cluster-administration/node-shutdown/

A reachable trusted Linux host can kill a complete cgroup tree and observe populated=0 after all contained descendants exit. The selected runtime must prove it cannot escape the cgroup and cannot be restored/resurrected later under old authority. Source: https://cdn.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html

An EC2 stop operation persists EBS while discarding RAM/instance-store data; starting ordinarily places the instance on a new host. This is useful substrate behavior, not proof of coordinated Claude checkpoint consistency or remote request cancellation. Resource identity and authoritative terminal state must be reconciled. Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html

## Smallest falsifiable qualification recipes

| ID | Test, using deterministic model transport where possible | Required oracle |
| --- | --- | --- |
| F-1 | Commit intent, lose reply, retry same Update and different Update ID with same logical key. | One scheduled effect; replayed successful Update response never triggers a second spawn. |
| F-2 | Outer Reset before/after accepted receipt and effect start; keep independent authority untouched. | Same original key; no redispatch, no synthetic unknown result. Attempt/fork guard preserved. |
| F-3 | Continue-As-New during duplicate submission and handler race. | Retained dedup/outstanding state, no lost accepted message or new ordinal. |
| F-4 | Remove/Reset ledger or prune closed workflow beyond retention while workspace restored earlier. | Refusal before SDK/effect; no automatic authority recreation. |
| F-5 | Effect succeeds, response lost, Activity timeout occurs. | Known provider receipt reconciles if definitive; arbitrary Bash parks; independent physical effect count remains one. |
| F-6 | Partition old host from Temporal while it can still reach effect witness; timeout or TTL expires. | Replacement blocked despite fresh Workflow/task/pod eligibility. No effect/process overlap. |
| F-7 | Force-delete old Pod/API object or detach volume without stopping host. | Replacement refused; deletion and detach not accepted as termination. |
| F-8 | Double-fork child, concurrent fork/migration and stale runtime identity. | Complete contained tree terminal receipt, no survivor; stale receipt refuses. |
| F-9 | Lost provider stop reply then query resource by bound immutable identity. | Resolve definitive terminal state or park; no new old resource identity guessed. |
| F-10 | Restore workspace before intent/claim; wake old host after new admission. | Independent authority refuses duplicate and stale capabilities cannot write/call outside policy. |
| F-11 | Candidate bounded gateway has stale epoch, direct network/file bypass and accepted in-flight provider call. | Every allowed destination rejects stale operations; bypass negative controls denied; in-flight known/unknown state correctly reconciles/parks. |
| F-12 | Repeat accepted checkpoint with changed call JSON types or input digest. | Exact original call/result only; mismatch refuses before effect/recovery. |

F-1 through F-4 can start as model-free Temporal integration qualification with an independent physical fake-effect counter; mock-only unit tests cannot prove actual Update/history/retry semantics. F-6 through F-11 require separately approved real runtime/host/storage qualification. Do not run old Phase 1 experiments again. Model transport counters can detect repeat inference without paid provider calls, while actual engine contract still needs separate later qualification.

## Source and query accounting

Temporal Docs connector discovered and successfully called three times. Queries covered Activity cancellation/timeout/late completion; idempotency/receipt/asynchronous completion; Entity Workflow intent/Continue-As-New/Reset/retention. Official primary pages were opened through web separately. Atlas wrapper query called twice and read wrapper once. Atlas feature retry_on_error source was inspected; it is a retry-count precedent, not this whole protocol.

One Atlas semantic example included Activity Attempt in an idempotency key. That snippet is rejected as unsuitable because a retry changes the key. Retrieved community/internal chunks were not used as primary design authority or persisted. The attempted safe-message-handler URL and etcd concurrency URL returned internal errors; no claim rests on either. Existing official handling-messages and Kubernetes/Linux sources supply the relevant verified boundaries.

No end-to-end independent-Entity intent plus original-pending Claude recovery plus physical two-host termination implementation was found in this bounded search. That is none_found exact protocol, not a claim no implementation exists anywhere. The composition remains proposed and tested at M1/M2/M4.

## Requested candidate corrections for lead

Make independent dispatch authority explicitly substrate-neutral: Temporal-owned retained Entity Workflow and protected unique SQL authority are competing recipes. Keep all no-redispatch, exact identity, accepted segment barrier, no-reset/recreation and physical termination requirements. Distinguish outer Workflow Reset from independent authority Reset. Add replayed Update permit negative and entity lifecycle/retention tests. Explain one Run survives Worker failure and no new Run ID is needed for pod/host placement. Do not replace physical termination with Workflow-ID uniqueness, storage mount status, lease expiry, heartbeats or hook success.
