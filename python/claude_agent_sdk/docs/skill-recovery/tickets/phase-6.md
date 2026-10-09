# Phase 6 tickets

### DSR-6.1 Record evidence and status for every assumption row

Status: OPEN

- Type: Documentation
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P6
- Blocked by: DSR-5.9
- Blocks: DSR-6.3
- Related: DSR-6.2
- Retires: A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08, A-09, A-10, A-11, A-12, A-13, A-14, A-15, A-16, A-17, A-18, A-19, A-20, A-21, A-22, A-23, A-24, A-25, A-26, A-27, A-28, A-29, A-30, A-31, A-32, A-33, A-34, A-35, A-36, A-37, A-38, A-39, A-40, A-41, A-42, A-43, A-44, A-45, A-46, A-47, A-48, A-49, A-50, A-51, A-52, A-53, A-54, A-55, A-56
- Informs: none
- Owner role: Plugin engineer

#### Context

PASS needs every row of the specification's assumption table settled. A row is settled when its status is verified at source with the proving artifact named, or when evidence contradicted it and the design changed in response. A row that is still untested, inferred, relayed, a proposed fix or an open decision is not settled.

The rebaselined specification retains A-01 to A-51 and adds A-52 to A-56 for review gaps. Scope removed rows stay present as superseded. Phase exit reviews update each retained proving obligation. This ticket reconciles the whole table so independent verification reads one consistent record.

The specification also marks several remedies as proposed fixes that no reviewer verified. The verify-design skill states that a remedy is a claim too, and a remedy needs its own verification before the document treats it as settled.

#### Problem

The phase reviews record partial evidence for rows that close in two or three phases. Without one reconciliation, a row can keep an early status, a proposed fix label can survive after its test passed, and the plan table can drift from the specification table.

Two rows, A-35 and A-36, close in Phase 7, after PASS. The definition of PASS says every row is settled. That text and the Phase 7 gate disagree unless the stated outcome excludes upstream submission and the harness port.

#### Scope

- Record a final status and a proving artifact or scope disposition for each of A-01 to A-56.
- Reconcile rows whose evidence came in parts, such as A-01, A-02, A-16, A-24, A-28 and A-41.
- Convert each proposed fix label in the specification text and the table into either a verified statement with its artifact, or a design change.
- Keep the plan's retirement table equal to the specification table.

#### Out of scope

- New tests or new measurements.
- Decisions that DSR-6.2 confirms.
- The verification pass. DSR-6.3 owns it.

#### Acceptance criteria

- [ ] Each of A-01 to A-56 is verified at source with a proving artifact, contradicted with a recorded design change, or superseded by the approved scope. No retained PASS row stays untested, inferred, relayed, proposed fix or an open decision. A-35 and A-36 remain explicitly outside PASS until Phase 7. Proof: all 56 row statuses and the stated PASS exclusions.
- [ ] Every proving artifact or scope disposition exists and shows the stated result. Proof: a 56 entry checklist, with A-35 and A-36 labeled outside PASS and every other entry checked against its artifact.
- [ ] A row whose evidence came in parts has all parts recorded, and the final status agrees with the latest part. Proof: the edited rows for A-01, A-02, A-06, A-08, A-15, A-16, A-17, A-22, A-24, A-28, A-29, A-30, A-32, A-40 and A-41.
- [ ] Each remedy that the specification labels as a proposed fix and not yet verified is either verified with the artifact named in its row, or removed by a recorded design change. No settled row rests on text that still says not yet verified. Proof: a search of the specification for the proposed fix label that returns only rows scoped out by the next criterion.
- [ ] A-35 and A-36 each carry a recorded scope statement that moves their retirement after PASS, with the Phase 7 ticket that settles them (DSR-7.1 for A-35, DSR-7.3 and DSR-7.2 for A-36). The statement is valid only if DSR-0.2 or DSR-6.2 records that the stated outcome excludes upstream submission and the harness port. Proof: the edited rows and the cited decision record.
- [ ] A row whose test could not run because of a missing environment, such as a declared untested limit, shows that status in plain words. The row counts as settled only if a recorded design change says so. Proof: the edited row and the design change.
- [ ] A row that earlier evidence contradicted names the design change with its date, and the rows that depend on the changed text are updated. Proof: the design change list and the edited rows.
- [ ] The plan retirement table and specification table hold the same 56 ids and consistent check text, including scope supersessions. Proof: a side by side listing.

#### Dependencies and blockers

- Blocked by DSR-5.9, the Phase 5 exit review.
- Blocks DSR-6.3.
- Related to DSR-6.2.
- The ticket retires every assumption id because it records the final evidence and status for each row.

#### Source evidence

- Specification, section *Assumptions and risks if wrong*, including its severity and reversibility definitions.
- Plan, section *Assumptions retired by milestone*.
- Ticket set index, section *What PASS means here*.
- Verify-design skill, section *A proposed remedy is a claim too*.

#### Open questions

- Operator: does the stated outcome exclude upstream submission and the harness port? The answer decides whether A-35 and A-36 count as settled for PASS.
- Plugin engineer: DSR-0.3 adds A-52 to A-56. Confirm retained coverage in DSR-2.3, DSR-4.2, DSR-3.2 and DSR-5.5; DSR-0.2 retires deferred A-52 and A-55 by scope rather than test evidence.
- The estimate is 4 points. If row additions arrive, split the table work from the reconciliation in review.

### DSR-6.2 Confirm that no open decision blocks the stated outcome

Status: OPEN

- Type: Decision
- Priority: High
- Estimate: 2 points (confidence 70 percent)
- Labels: Type: Decision, Topic: Assumptions
- Parent: DSR-P6
- Blocked by: DSR-5.9
- Blocks: DSR-6.3
- Related: DSR-6.1
- Retires: none
- Informs: A-14, A-17, A-35, A-36, A-37, A-38
- Owner role: Operator

#### Context

PASS needs two things beyond settled rows. No open decision may block the stated outcome, and each decision in the plan's M0 list that the approved scope needs must have a named owner and a recorded answer.

The M0 list retains its stable decision ids. DSR-0.2 excludes keyed service retention, and DSR-0.10 is SUPERSEDED rather than missing an answer. Every retained owner, budget, isolation, reset and rollout decision remains required. The specification's Open issues list other choices, such as namespace retention (OI-10).

#### Problem

A decision that has an owner and no answer, or an answer that exists only as a model draft, still blocks the stated outcome. The verify-design skill gives PASS only when no unresolved decision blocks the outcome. DSR-0.2 fixes the version 1 scope, which decides which decisions the outcome needs.

#### Scope

- A decision matrix that lists each M0 item (a) to (j) and each Open issue whose status is OPEN and which asks for a decision.
- For each row: whether the approved scope needs it, the owner role, and where the recorded answer sits.
- A confirmation by the owner that the answer on record is the owner's own.

#### Out of scope

- Making a decision for its owner. Each owner answers.
- Reopening the version 1 scope. DSR-0.2 owns it.
- Phase 7 decisions that the outcome does not need. The matrix lists them as out of the outcome.

#### Acceptance criteria

- [ ] The matrix has one row for each of M0 (a) to (j) and for A-37 retention (OI-10), with the scope clause from DSR-0.2 that makes the decision needed or not needed. Proof: the matrix in a decision record.
- [ ] Every row marked needed names an owner role and points to a dated recorded answer. No needed row reads pending. Proof: the matrix with a link to each answer.
- [ ] Each recorded answer is the owner's own statement, or the owner confirmed it in writing. A draft by the verifier or the lead does not count. Proof: a reference to each confirmation.
- [ ] A row marked not needed states why the outcome does not use it. Item (e) and the second half of item (b) are listed this way only if the outcome excludes the harness port and upstream submission. Proof: the matrix and the scope clause.
- [ ] If a needed decision lacks an answer, this ticket stays open, a new ticket names the owner and the missing answer, and DSR-6.3 does not start. Proof: the new ticket or the closed matrix.

#### Dependencies and blockers

- Blocks DSR-6.3.
- Related to DSR-6.1, which treats A-35 and A-36 consistently with this matrix.
- Needs the decision records from DSR-0.1, DSR-0.2, DSR-0.4, DSR-0.5, DSR-0.6, DSR-0.7, DSR-0.8, DSR-0.9 and DSR-0.10. The records exist before this ticket reads them.

#### Source evidence

- Plan, section *Milestones*, M0, for the list (a) to (j) and the gates.
- Specification, section *Open issues*, and the rows A-14, A-17, A-35, A-36, A-37 and A-38 of the assumption table.
- Ticket set index, section *What PASS means here*.
- Verify-design skill, section *Verdicts*.

#### Open questions

- Operator: who confirms an answer when its owner role has no named person? The assumption table lists many owners as unowned.
- Operator: does a decision (c) that declares an untested limit count as an answer for PASS?

### DSR-6.3 Run the independent verification pass on the evidenced design

Status: OPEN

- Type: Verification
- Priority: High
- Estimate: 4 points (confidence 60 percent)
- Labels: Type: Verification, Topic: Assumptions
- Parent: DSR-P6
- Blocked by: DSR-6.1, DSR-6.2
- Blocks: DSR-6.4
- Related: none
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

PASS is a verify-design verdict on the specification and the plan, reached on evidence. The skill requires two fresh reasoning contexts: a contract evidence verifier and an adversarial system verifier. Each receives the raw verification contract, stable source identities, the scoped artifacts and read only tools. Neither receives the lead's answer or the other's conclusions.

For a Temporal design the skill also invokes the Temporal design review skill as domain evidence. The lead records the outcome in a verification manifest. The manifest gate checks the manifest, and the proof of load script checks that the transcript shows a successful `Skill` call for the review. Earlier critiques of revisions 4 and 5 loaded the skill by file read, so their load stayed unproven. The critique of revision 6 ran through the `Skill` tool.

The specification and the plan each have an evidence manifest and an evidence gate script.

#### Problem

Earlier rounds checked drafts. They did not check a design that carries evidence for each assumption. No pass has reviewed revision 6 or its later revisions, and a pass that cannot prove its domain review ran gives a weaker verdict.

#### Scope

- One complete verify-design pass on the final evidenced specification and plan, with fresh verifiers.
- The manifest, both gate scripts and the report the skill requires.
- A read only pass. Edits belong to DSR-6.4.

#### Out of scope

- Resolving findings. DSR-6.4 owns it.
- Implementation changes or any message to an outside system.
- Customer facing guidance.

#### Acceptance criteria

- [ ] Before it dispatches the verifiers, the lead states the verification contract in the transcript: the target artifacts, the claims, the governing sources, the fork repository identity at the pinned commit with a fresh head check, the exclusions, and what counts as PASS, CONDITIONAL and FAIL. Proof: the transcript text.
- [ ] The lead confirms to the user in the transcript that the Temporal design review skill was discovered, and names the string it was discovered under, or records another outcome with its reason. Proof: the transcript text.
- [ ] The contract evidence verifier and the adversarial verifier each run in a new context that took no part in earlier rounds and in no edit of the documents. Each receives only the raw contract, the source identities and the scoped artifacts. Proof: the verifier identities and the prompts in the report.
- [ ] The Temporal design critic is invoked through the Skill tool by the lead or by a named verifier role. Proof: the proof of load script exits 0 and reports the row as proven, with the lead transcript and each verifier role transcript passed in. A result of not proven or fabrication fails this criterion, and the pass repeats on a harness that the script can check.
- [ ] The verification manifest conforms to the schema and holds one `temporal-design-review` row with outcome `applied`, the `discovered_as` name, the `invoked_by` role, and either `finding_refs` that point at claim ledger entries or `no_findings` true. The manifest gate exits 0. Proof: the gate output saved with the report.
- [ ] The report copies the gate's disclosure sentence unchanged and states the proof of load result. Proof: the report text beside the gate output.
- [ ] The evidence gate passes for the specification and for the plan, each ending with `RESULT: PASS`, after the final edits and before the verifiers read the documents. Proof: the captured output for the specification with its manifest and for the plan with its manifest.
- [ ] The lead reproduces the decisive source reads and confirms that each stable source identity still matches, before it accepts a verdict. Proof: the recorded reads and the identity comparison.
- [ ] The report classifies each finding as material, nonmaterial or incorrect. Each inferred correction carries its scope anchor, mandatory basis, failure consequence and source role. Proof: the finding ledger.
- [ ] The report holds one verdict (PASS, CONDITIONAL or FAIL), and reports BLOCKED separately for evidence that could not be accessed. A manifest gate failure withholds the verdict and is reported as a process blocker. Proof: the report.

#### Dependencies and blockers

- Blocked by DSR-6.1, which records the evidence for every row.
- Blocked by DSR-6.2, which confirms that no needed decision is open.
- Blocks DSR-6.4.

#### Source evidence

- Verify-design skill, sections *Run independent verification*, *Record and gate the domain review outcome* and *Verdicts*.
- Specification, section *Rigor tier*, which requires a further verify-design pass.
- Plan, section *Verification handoff*.
- Ticket set index, section *What PASS means here*, item 3.

#### Open questions

- Resolved by the PASS scope statement in the ticket set index: the plan's earlier pass after the M0 decisions and before M1 is dropped, and the Phase 1 real model evidence replaces it. DSR-0.3 removes it from the plan.
- Operator: which harness runs the pass? Only a Claude Code transcript can give a proven load, and a Codex run gives not proven.
- Budget owner: do the verifier runs use a budget that DSR-0.4 covers? The verifiers read documents and do not call a real model for the design.

### DSR-6.4 Resolve findings and reach a PASS verdict

Status: OPEN

- Type: Verification
- Priority: High
- Estimate: 5 points (confidence 40 percent)
- Labels: Type: Verification, Topic: Assumptions
- Parent: DSR-P6
- Blocked by: DSR-6.3
- Blocks: DSR-7.1, DSR-7.2
- Related: none
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

DSR-6.3 returns a verdict. A verdict other than PASS carries findings that the lead classifies and resolves, and then a new pass checks the corrected documents. PASS needs every material claim confirmed, an internally coherent and implementable design, and no unresolved decision that blocks the stated outcome. CONDITIONAL names assumptions, decisions or bounded corrections. FAIL names contradicted or unsafe claims.

The skill warns that a reviewer's remedy is a claim too. A second CONDITIONAL result that comes only from unverified remedies is a process failure in the earlier reconciliation. Earlier rounds in this pack wrote many remedies as proposed fixes for that reason.

#### Problem

A single loop of fixes can write unverified remedies into the documents as settled prose. A verdict can also close on a document that later changes. The loop needs fixed rules for what counts as resolved and when it ends.

#### Scope

- Classify and resolve each finding from each pass.
- Verify each reviewer remedy before it enters the specification or the plan.
- Repeat the full pass of DSR-6.3 on each corrected revision until the verdict is PASS.
- Record the PASS for a named revision of both documents.

#### Out of scope

- Implementation changes to the plugin.
- Upstream submission and the harness port. Phase 7 owns them.
- A change of scope that DSR-0.2 owns. A scope change goes back to its owner.

#### Acceptance criteria

- [ ] Each finding of each pass is classified as material, nonmaterial or incorrect, with the provenance fields that the skill requires for an inferred correction. Each material finding has a recorded resolution (a design change, new evidence or a decision with an owner), and each incorrect finding cites the stronger evidence. Proof: the finding ledger.
- [ ] Every reviewer remedy is verified before it is written into the specification or the plan as an adopted correction. The verification is a direct source read, a primary documentation check or an independent agent. A remedy that has no verification record stays labeled as a proposed fix, and the next pass tests it. Proof: a remedy ledger with one verification record for each adopted remedy.
- [ ] At PASS, no material claim rests on a remedy that is still labeled as a proposed fix. Proof: a search of both documents for the label, with each hit listed and judged nonmaterial in the final report.
- [ ] Each corrected revision gets a new full pass with fresh verifiers, a new manifest, a passing manifest gate, a proven load and a passing evidence gate for each document, as in DSR-6.3. Proof: one record per revision with the verdict and the gate outputs.
- [ ] A CONDITIONAL verdict reopens each named assumption, decision or bounded correction as a new ticket with a new id. The new tickets block this ticket. The ticket set index gains rows for the new tickets, because the index defines the allowed ids. Proof: the new tickets and the index rows.
- [ ] A FAIL verdict leads to a recorded design change, an update of the rows in DSR-6.1 and a new pass. A BLOCKED result is not treated as PASS and leads to a ticket for the evidence blocker. Proof: the design change record and the evidence blocker ticket.
- [ ] The final PASS report states that every material claim is confirmed and that no unresolved decision blocks the stated outcome. It names the revision of the specification and of the plan that it verified, by digest. A later edit to either document voids the PASS until a new pass runs. Proof: the report and the digests.

#### Dependencies and blockers

- Blocked by DSR-6.3, the first full pass.
- Blocks DSR-7.1 and DSR-7.2, which start after PASS.

#### Source evidence

- Verify-design skill, sections *Reconcile findings*, *A proposed remedy is a claim too*, *Gate inferred corrections by provenance* and *Verdicts*.
- Ticket set index, section *What PASS means here*.
- Plan, section *Verification handoff*, for the remedies that earlier rounds left as proposed fixes.

#### Open questions

- Stop rule, proposed and open for operator approval: if the second full pass does not return PASS, the loop stops and the operator decides whether to reduce the scope through DSR-0.2, accept a CONDITIONAL verdict with named conditions, or continue with a stated budget. The skill itself sets no limit.
- The estimate is 5 points because the loop has no fixed length. Split it in review into a first resolution round and a repeat rule.
