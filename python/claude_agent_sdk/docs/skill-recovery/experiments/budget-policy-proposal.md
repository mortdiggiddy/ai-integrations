# Budget policy for bounded recovery proofs

Status: CORE PLANNING LIMITS CONFIRMED (2026-10-02); request output and phase token limits remain proposed. This policy grants no model execution permission, changes no monitor and closes no live budget acceptance criterion. The local operator is the confirmed proof budget owner and model/cap change authority.

[The enforcement decision proposal](budget-enforcement-disposition.md) owns the next decision: retain strict preventive criteria, distinguish planning limits from live authorization, settle monthly scope/billing, and scope an offline request admission/accounting proof. Its recommendation does not select a new transport or approve another invocation.

## Planning limits and necessary spend

| Boundary | Planning limit | Scope |
| --- | --- | --- |
| Model | `claude-haiku-4-5-20251001` only | No alias, substitution or provider fallback |
| Currency per logical test | USD 1.00 list estimate | All segments, continuations and retries together |
| Input per logical test | 100,000 tokens | All requests, including cached input categories |
| Output per logical test | 8,192 tokens | All requests, including thinking where reported as output |
| Output per provider request | At most 4,096 tokens and remaining output allowance | Unconfirmed proposal; no assertion that this CLI enforces it across internal continuations |
| Current proof phase | USD 20.00 list estimate confirmed for planning; 2,000,000 total tokens unconfirmed | Completed usage plus outstanding reservations; no live allocation |

The operator confirmed the exact model, logical test USD/input/output limits and USD 20 phase planning limit. These are guardrails, not necessary spend or a target. The [exact proposed offline batch](budget-enforcement-disposition.md#exact-proposed-offline-batch) needs USD 0 provider spend. Before any later live authorization, estimate the actual requests, input/output and allowed charged categories for its specific recovery scenario, then justify a small allowance against that estimate. Do not derive a test allocation from a personal monthly maximum. These limits are not calibrated for whole repository coding or assessment workloads. An output ceiling of 64 previously produced an output-limit error and internal continuation; repeating that setting is not a reasonable default for longer proof tasks. Neither increasing the output ceiling nor the currency allowance repairs the unproved preventive request boundary.

Official [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), checked on 2026-10-02, lists Haiku 4.5 at USD 1 per million ordinary input tokens and USD 5 per million output tokens; one-hour cache writes are USD 2 per million. The proposed 100,000 input and 8,192 output envelope is about USD 0.14096 at ordinary input prices, or USD 0.24096 if every input token is a one-hour cache write. This gives margin within the USD 1 allowance for this narrowly stated token envelope. It excludes other paid features, price changes and actual subscription billing terms. Currency and token limits both apply independently.

The earlier monthly figure is the operator's personal limit, not an organization limit, proof allocation or available headroom. Spend from other work and actual billing remain outside this local harness. No live phase allocation exists. Phase 5 requires a separate allocation and acceptance record; this policy allocates nothing to Phase 5.

## Offline admission and reconciliation contract

Before any future authorized launch, reserve the full approved logical test allowance against its phase. Use exact integer currency units and integer token counts. Bind a unique admission to the exact model, phase, logical test and immutable approved caps. A segment, retry or replacement process remains within that admission; it does not reset usage. A persistent admission store must serialize overlapping processes within its explicitly supported host topology. Local serialization is not a distributed ownership or fencing guarantee.

A reservation survives process exit, timeout, lost output and unknown accounting. None of those events refunds it. Complete verified accounting can reconcile a reservation once. An identical repeated reconciliation is harmless; conflicting reconciliation blocks further admissions. Cost beyond the reserved amount is recorded in full and blocks continuation and further admissions pending investigation. Preserve provider billing uncertainty separately from CLI list estimates. A budget reservation does not establish actual invoice accounting.

Input categories must be disjoint when summed: ordinary input, cache reads and cache writes. Do not count a reported thinking subset twice inside output. Missing usage, uncertain category semantics or an unknown model cannot be treated as zero. Show both consumed and unresolved reserved totals in evidence.

Paid execution remains disabled. The current subscription CLI can perform internal continuations before host result observation. A host reservation, a result-based token counter and a reactive removal monitor do not establish a hard preventive provider request, token or currency cap. If the route cannot enforce the approved boundary, obtain an explicit budget design decision rather than treating this proposal as enforcement. The ambiguous overage stop remains unchanged.

## Meaningful offline checks to implement

The local ledger implementation and measured checks are now recorded in [offline budget ledger evidence](../evidence.md#offline-budget-ledger-2026-10-02). The list below retains the proposed proof boundaries. The separately configured shared monthly boundary is not implemented: the ledger models independent phases only, and neither monthly scope nor headroom is inferred. Live allocations and preventive provider enforcement remain open.

- Two independent processes contend for the last available allowance; only one admission succeeds, and reopening the store preserves it.
- A process exits after reservation with no final accounting; a replacement cannot refund, repeat or bypass that admission, including at phase rollover.
- Several resumed segments and retries reconcile against one logical test; cumulative input, output and cost never reset between them.
- Identical reconciliation is idempotent; conflicting, malformed, incomplete or over-reservation accounting blocks subsequent admission.
- Each token category is charged once; thinking as an output subset is not double counted, and missing usage is unresolved.
- A different model, changed caps or reused admission identity refuses before transport startup.
- Current phase and Phase 5 totals remain separate, while a separately configured shared monthly boundary includes both and retains unresolved older reservations.
- A deliberately insufficient allowance produces a nonpassing outcome before simulated transport. No live transport or credentials are needed for these checks.

The linked evidence identifies the checks executed offline and the remaining gaps. Local ledger checks establish only offline accounting behavior. [Real model harness acceptance](../work-items.md#real-model-harness), [billing reconciliation](results/published/subscription-sdk-controls/overage-source-trace.md) and the mandatory phase review remain open. Both existing consumed single use reservations must remain untouched.

## Current acceptance allocation (2026-10-03)

The [approved separation decision](budget-enforcement-disposition.md#approved-separation-of-experiment-authorization-and-preventive-budgeting-2026-10-03) governs current sequencing. Phase 1 may prepare a separately approved monitored recovery experiment before strict provider enforcement is proved. Planning limits, unresolved billing and consumed reservations stay unchanged. The strict preventive request/token/currency and cumulative accounting checks remain required at final Application Workflow acceptance; they are not completed, discarded or inferred from reactive interruption. No live invocation or new allocation is authorized by this rebaseline.

## Implemented local storage contract

`tests/helpers/budget_ledger.py` uses standard library SQLite, integer micro USD (one million units per USD) and integer token counts. A fresh disposable ledger requires explicit initialization and exclusive file creation; reopening uses SQLite `mode=rw` and refuses missing storage. Initialization refuses an existing file. Every operation opens a connection, uses `BEGIN IMMEDIATE` and `synchronous=FULL`, and closes the connection. Competing admissions see one committed state. A lock timeout or I/O failure refuses rather than creating replacement storage.

The supported topology is cooperating local processes on one host, all using the same retained database and SQLite journal on a local filesystem with reliable SQLite locking and fsync. Tested process replacement does not require the original process to survive. Network filesystems, multiple hosts, distributed ownership/fencing, power loss, database deletion or snapshot rollback, hostile writers and arbitrary surviving child processes are outside this proof. The host owns database path continuity, storage integrity, permissions and process containment. Copying the database into another execution directory would split its budget and is not a supported replacement route.

Phase policy and logical test limits bind an exact configured model, not an alias or fallback. Logical test identity is unique across phases. `reserve` holds the entire logical test envelope, and `begin_segment` records each unique segment or retry before simulated transport. A replacement reopens the same reservation and cannot continue while a prior segment lacks accounting. Segment reconciliation supplies deltas for that segment, never a resetting cumulative report. Full test consumption is the sum of all reconciled segments. `finish` requires at least one accounted segment and no unresolved segment; only this explicit final operation releases unused allowance, while permanently closing the original identity.

Snapshots distinguish known consumed cost/tokens from the unresolved reserved remainder. While a test is open, consumed usage plus its held remainder charges at least the full original envelope; excess usage is retained in full. Process exit, cancellation, timeout and missing final output do not reconcile or refund a segment. Unknown usage appears as null with `accounting_status=unresolved` in harness records. It is not a zero cost completion. Complete identical reconciliation is idempotent, including after test closure. Conflicting, malformed, missing or excessive submitted accounting persists a ledger wide admission block; no automatic repair/refund API exists.

Input accounting requires explicit disjoint ordinary, cache read and cache write counts. Output includes its reported thinking subset, which is validated but never added twice. An adapter for a real stream must prove those category meanings and complete coverage before submitting reconciliation. The offline harness rounds reported fixture costs upward to micro USD; approved caps require exact micro USD precision. This is fixture/list estimate accounting, not invoice verification.

The harness remains simulation only and always refuses paid execution. Its defaults are configurable offline examples; exact Haiku selection still requires explicit configuration. Phase 5 requires a distinct configured phase and test identity, has no live allocation and cannot erase an earlier reservation. No account or organization monthly spend counter exists. The monthly figure is now classified as a personal limit; remaining headroom, historical billing and preventive provider request/token/currency boundaries remain unresolved.
