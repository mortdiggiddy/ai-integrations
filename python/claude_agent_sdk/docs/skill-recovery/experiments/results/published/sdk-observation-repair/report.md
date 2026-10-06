# Bounded observation repair completion

Verdict: **PASS** for the repaired probe observation classifier and its cooperating local host/controller dependencies. Contract: [contract.md](contract.md). Prior verification FAIL and exhausted correction cycle remain preserved in their original directories. This is a fresh scope with one initial independent pass and zero production correction cycles.

| Evidence | Result |
| --- | --- |
| Focused baseline, existing `host_session_offline.py` | 105 passed, four existing warnings, 2.99 seconds, exit 0 |
| Actual `sdk_shutdown_probe.py --output .../sdk-observation-repair/actual-sdk` | One invocation, exit 0; no prompt/model call |
| `/root/observation_contract` | PASS; 105 focused cases and 121 supplemental checks in pinned Python 3.13 |
| `/root/observation_adversarial` | PASS; isolated final 165 passed, four warnings, 7.26 seconds |
| Lead final required focused rerun | 105 passed, four existing warnings, 3.17 seconds, exit 0 |
| Saved actual observation/report correspondence | PASS; no additional SDK invocation |

See [contract report](contract/report.md), [adversarial report](adversarial/report.md), [actual report](actual-sdk/report.json), [final lead output](lead-final-output.txt) and [source manifest](pre-verification-source-hashes.json). Both verifiers received raw requirements in fresh independent contexts and stayed read only in the real tree. Adversarial modifications ran in an isolated copy. Author fixture failures occurred before the green baseline. Independent fixture diagnostics and the affected contract verifier's pinned-runtime rerun are retained. After dispatch only isolated verification fixtures changed, with no production correction.

Explicit complete error-free snapshots recorded Claude PID 8/start `22811257` after connection and its absence after public interrupt/disconnect. SDK completion and sampled absence are distinct from the host's exit 137, stopped state and verified resource removal. Fresh admission was refused before cleanup and replacement admitted afterward. This proves neither graceful engine shutdown nor live recovery, inference interruption, distributed fencing or production containment.

Missing, malformed, incomplete and unreadable inventories now remain unresolved; enumeration/per-process failures are recorded, including uncertain disappearance during collection. Every relevant observed identity is compared by PID/start. The previously successful adversarial missing-disconnect case now fails conservatively despite SDK control completion. Replacement still requires authoritative host receipts.

The fixed installed image, SDK/CLI pins, network none and disposable storage were used without dependency synchronization, installation, build/pull, credentials, model calls or container Docker socket. Ruff execution is unproved because the image's wrapper has no executable (`RuffNotFound`); no lint/format pass is claimed. Host, controller, runner, spec and plan are unchanged in this repair. Broader budget/provider, recovery, engine lane and phase exit criteria remain open. No commit or push occurred.

Record checks passed: four canonical documents and 59 assumption IDs; all 69 local ticket blocks; all 69 map status/title/dependency entries and five affected index rows. Report links, new public scope boundary, preserved code/spec/plan/budget hashes and both repositories' `git diff --check` passed. Branch remains `design-base` at published HEAD `6c4684bade297720e74dd4f0bf5af5b293bcf53c`. Prior uncommitted work is retained.

Next concrete step: resolve the recorded budget/provider enforcement decision before separately scoping live deferred Write proof.
