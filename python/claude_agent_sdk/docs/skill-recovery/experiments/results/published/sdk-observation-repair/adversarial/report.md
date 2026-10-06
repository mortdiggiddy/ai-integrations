# Independent adversarial containment report

Verifier identity: `/root/observation_adversarial`. Verdict: **PASS** for the scoped observation repair and cooperating local host admission contract. No unresolved material or nonmaterial product finding. The verifier remained read only in the real tree; supplementary modifications ran in a temporary copy. This report records the verifier's returned evidence, with runtime paths normalized in archived text.

| Command and working directory | Exit and count |
| --- | --- |
| `python3 python/claude_agent_sdk/docs/skill-recovery/experiments/host_session_offline.py`, real repository root | 0; 105 passed, four warnings, 3.08 seconds |
| Same command, isolated copy after fixture correction | 0; 162 passed, four warnings, 7.33 seconds |
| Same command, final isolated copy | 0; 165 passed, four warnings, 7.26 seconds |

The final isolated run comprises 105 existing focused cases, 57 fresh end-to-end `host_probe` variants and three fresh collection-race cases. All SDK behavior is scripted. No actual SDK invocation, model call, install, build, pull, credential access or version-control write occurred in this verifier context.

| Contract branch | Direct evidence |
| --- | --- |
| Missing post-disconnect inventory | `test_fresh_adversarial_host_probe[missing_after_disconnect]` returns exit 1, control completion true, process validity/absence false and the exact unresolved inventory diagnostic. |
| Complete, explicit observation contract | Missing/invalid enumeration, completeness, errors, PID and row lists, version, PID, start, state and comm variants reject through the full driver. |
| Observation file failure | Truncated JSON, non-object content and injected observation-file `PermissionError` produce failed reports. |
| Every relevant identity | Parent, descendant and zombie survival produce the surviving-identity diagnostic. PID reuse with different start, order-only changes and unrelated processes retain valid behavior. |
| Collector races | Existing enumeration/stat/comm/identity/deadline cases and fresh comm ENOENT, repeated-stat ENOENT and partial-enumeration timeout retain uncertainty. |
| Independent SDK completion | Failed interrupt, closure timeout, truthy completion fields, missing control fields and explicit connect/close errors reject completion independently of process absence. |
| Host receipts remain authoritative | Daemon callbacks inspect receipt null/termination zero before kill, termination one/removal zero before removal, and independent cleanup before replacement. |
| Fresh and stale admission | Fresh runner/attempt refuse before cleanup. Existing stale owner/observation/teardown and owner-exit cases pass; replacement requires verified stopped/removal receipts. |
| Partial teardown | Wait, removal, daemon enumeration and retained-resource faults prevent replacement. |
| Unrelated interfaces | Normal results, original structured result/resume, session-specific stop and error-result cases remain green. |

[Final challenge source](challenge-final.py.txt), [full final output](adversarial-final-output.txt), [branch outcomes](branch-results.json) and [missing inventory reproduction](missing-after-disconnect-report.json) retain the evidence. Final original challenge SHA256 is `45bcdec7a9cd68698a7aaf00812e97d165f035d37d5a327e45b1c20706aab5d4`. [Before](before-hashes.json) and [after](after-hashes.json) manifests show zero changes to real Python source/test/experiment files.

The first isolated fixture attempted `HostSession.snapshot()` inside a daemon callback already running under teardown's SQLite `BEGIN IMMEDIATE`. Nested transaction contention caused timeouts and the 45 second offline observation deadline expired. The failed command returned nonzero. The verifier corrected only its temporary fixture: plain SQLite reads for inspection and selected representative admission assertions. [Initial failure log](adversarial-output.txt), [first passing corrected source](challenge-corrected.py.txt) and [output](adversarial-output-corrected.txt) are preserved. [Reconstructed initial source](challenge-initial-reconstructed.py.txt) is explicitly an inverse reconstruction of fixture edits, not a captured original. No production correction follows from this fixture defect.

The verifier independently read the lead-owned actual SDK observations and command/host receipts: complete inventories show Claude PID 8/start `22811257` after connection and its sampled absence after disconnect; host receipt separately establishes exit 137, `Running=false`, `Pid=0` and removal. It did not repeat the actual invocation or read the other verifier's conclusions.

No operator path, PII, workspace marker or private ticket identifier was introduced in the supplementary challenge/extracted reports. Temporal design review is inapplicable to this local Claude lifecycle/process diagnostic. Historical FAIL archives remain intact. This scoped PASS does not establish graceful shutdown, inference interruption, real recovery, distributed fencing or broader work item completion.
