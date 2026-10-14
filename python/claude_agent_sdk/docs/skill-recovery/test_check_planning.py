"""Source-only closure guard regression tests; no SDK, sync or server required."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("planning", Path(__file__).with_name("check_planning.py"))
planning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planning)


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.owner = self.root / "proposals/distributed-recovery/2026-10-08"
        self.owner.mkdir(parents=True)
        self.record = self.owner / "dsr-0.6-closure.json"
        content = "# Confirmed decision\n\nSynthetic owner record for guard qualification only.\n"
        (self.owner / "dsr-0.6-configuration.md").write_text(content)
        self.ref = {"ref": "proposals/distributed-recovery/2026-10-08/dsr-0.6-configuration.md#confirmed-decision", "sha256": hashlib.sha256(content.encode()).hexdigest()}
        self.decisions = {f"BD-{n}": [f"BD-{n}", "Open"] for n in range(1, 7)}
        criteria = {
            label: {"approved": True, "answers": {field: "Selected exact binding in confirmed owner" for field in fields}, "evidence": [self.ref]}
            for label, fields in planning.CLOSURE_FIELDS.items()
        }
        criteria["refusal"]["answers"] = {field: "refuse" for field in planning.CLOSURE_FIELDS["refusal"]}
        criteria["refusal"]["answers"]["restore_permission"] = "never"
        criteria["assumptions"]["answers"] = {
            field: {"disposition": "retained", "interim_claim": "Decision only; physical Phase 4 proof required"}
            for field in planning.CLOSURE_FIELDS["assumptions"]
        }
        criteria["configuration"]["answers"]["runtime_pins"] = {"synthetic-runtime": "1.2.3+exact"}
        criteria["configuration"]["answers"]["workload_bounds"] = {
            "sessions": 1, "pending_calls": 1, "effects": 1,
            "workspace_bytes": 3000000, "model_output_bytes": 65536,
            "raw_result_bytes": 65536, "envelope_bytes": 65536,
            "index_bytes": 65536, "scratch_bytes": 65536,
            "processes": 2, "cpu_seconds": 60, "deadline_seconds": 600,
            "clock_skew_seconds": 1, "recovery_window_seconds": 86400,
        }
        criteria["configuration"]["answers"]["retention"] = {
            "minimum_seconds": 604800, "extend_while_referenced": True,
        }
        self.data = {
            "ticket": "DSR-0.6",
            "answers": {
                "decisions": {key: {"approved": True, "answer": "Applicable DSR-0.6 choice selected; broader candidate question deferred", "evidence": [self.ref]} for key in self.decisions},
                "criteria": criteria,
                "qualification_gates": {key: {"status": "unexecuted", "owner": "Project maintainer", "required_evidence": "Separately authorized physical native/provider qualification"} for key in ("DSR-4.3", "Q-7", "Q-15")},
            },
            "approval": {"status": "approved", "by": "Synthetic approving operator", "date": "2026-10-14"},
        }
        self.section = "\n".join("- [x] criterion" for _ in range(6))

    def write(self, data=None):
        data = copy.deepcopy(data or self.data)
        data["approval"]["answers_sha256"] = hashlib.sha256(json.dumps(data["answers"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.record.write_text(json.dumps(data))

    def errors(self, status="DONE"):
        return planning.closure_errors(self.root, status, self.decisions, self.section)

    def test_open_requires_no_artifact(self):
        self.assertEqual(self.errors("OPEN"), [])

    def test_premature_done_missing_record(self):
        self.assertTrue(self.errors())

    def test_confirmed_planning_closure_preserves_broader_open_decisions(self):
        self.write()
        self.assertEqual(self.errors(), [])

    def test_partial_or_unapproved_answers_fail(self):
        for mutation in ("missing", "placeholder", "unapproved", "missing_evidence"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                configuration = data["answers"]["criteria"]["configuration"]
                if mutation == "missing":
                    del configuration["answers"]["encryption_keys"]
                elif mutation == "placeholder":
                    configuration["answers"]["license_fit"] = "TBD"
                elif mutation == "unapproved":
                    configuration["approved"] = False
                else:
                    configuration["evidence"] = []
                self.write(data)
                self.assertTrue(self.errors())

    def test_stale_or_unapproved_attestation_fails(self):
        self.write()
        data = json.loads(self.record.read_text())
        data["approval"]["status"] = "proposed"
        self.record.write_text(json.dumps(data))
        self.assertTrue(self.errors())
        self.write()
        data = json.loads(self.record.read_text())
        data["answers"]["criteria"]["isolation"]["answers"]["level"] = "Changed binding"
        self.record.write_text(json.dumps(data))
        self.assertTrue(self.errors())

    def test_changed_owner_bytes_and_nonowner_reference_fail(self):
        self.write()
        (self.owner / "dsr-0.6-configuration.md").write_text("# Changed\n")
        self.assertTrue(self.errors())

    def test_checkbox_only_or_fabricated_qualification_fails(self):
        self.write()
        self.section = "- [x] one criterion"
        self.assertTrue(self.errors())
        self.section = "\n".join("- [x] criterion" for _ in range(6))
        data = copy.deepcopy(self.data)
        data["answers"]["qualification_gates"]["Q-15"]["status"] = "qualified"
        self.write(data)
        self.assertTrue(self.errors())

    def test_unapproved_decision_and_nonowner_reference_fail(self):
        data = copy.deepcopy(self.data)
        data["answers"]["decisions"]["BD-2"]["approved"] = False
        self.write(data)
        self.assertTrue(self.errors())
        data = copy.deepcopy(self.data)
        data["answers"]["criteria"]["checkpoint"]["evidence"] = [{"ref": "other.md#confirmed", "sha256": "0" * 64}]
        self.write(data)
        self.assertTrue(self.errors())

    def test_nonfinite_bounds_and_short_retention_fail(self):
        for field, value in (("workload_bounds", "finite"), ("runtime_pins", "latest"), ("retention", {"minimum_seconds": 3600, "extend_while_referenced": False})):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["answers"]["criteria"]["configuration"]["answers"][field] = value
                self.write(data)
                self.assertTrue(self.errors())

    def test_answered_row_needs_evidence_even_if_ticket_open(self):
        self.decisions["BD-1"][-1] = "Answered EV-1"
        self.assertTrue(self.errors("OPEN"))
        self.write()
        self.assertEqual(self.errors("OPEN"), [])

    def test_runtime_pin_map_rejects_floating_and_nonstring_identities(self):
        for value in ("latest", "stable", "1.2", "1.2.*", ">=1.2.3", "main", "HEAD", 1, True, None):
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["answers"]["criteria"]["configuration"]["answers"]["runtime_pins"] = {"Temporal Server": value}
                self.write(data)
                self.assertIn(
                    "DSR-0.6 closure: runtime pins need exact version, commit or content digest strings",
                    self.errors(),
                )

    def test_runtime_pin_map_preserves_exact_version_revision_and_digest(self):
        for value in ("1.2.3", "v1.2.3-rc.1+build.7", "1.2.3rc1", "1.2.3.post1", "1.2.3.dev1", "a" * 40, "sha256:" + "a" * 64):
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["answers"]["criteria"]["configuration"]["answers"]["runtime_pins"] = {"Synthetic runtime": value}
                self.write(data)
                self.assertEqual(self.errors(), [])


    def test_duplicate_json_keys_are_rejected_before_approval_validation(self):
        self.write()
        original = self.record.read_text()
        for needle, replacement in (
            ('"ticket": "DSR-0.6"', '"ticket": "invented", "ticket": "DSR-0.6"'),
            ('"status": "approved"', '"status": "unapproved", "status": "approved"'),
        ):
            with self.subTest(key=needle):
                self.record.write_text(original.replace(needle, replacement, 1))
                self.assertTrue(any("duplicate JSON key" in error for error in self.errors()))
        self.record.write_text(original)
        self.assertEqual(self.errors(), [])

    def test_nonfinite_json_constants_are_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["answers"]["criteria"]["configuration"]["answers"]["license_fit"] = value
                self.write(data)
                self.assertTrue(any("invalid JSON constant" in error for error in self.errors()))

    def test_text_decisions_reject_scalar_and_collection_substitutions(self):
        for label, field in (("checkpoint", "substrate"), ("portable_cases", "finite_rig_holder"), ("isolation", "security_holder"), ("configuration", "license_fit")):
            for value in (1, True, ["Selected binding"]):
                with self.subTest(label=label, value=value):
                    data = copy.deepcopy(self.data)
                    data["answers"]["criteria"][label]["answers"][field] = value
                    self.write(data)
                    self.assertIn(
                        f"DSR-0.6 closure: {label} answer fields require text or declared structured values",
                        self.errors(),
                    )


    def test_nested_decision_and_qualification_descriptions_require_text(self):
        for location in ("decision", "interim_claim", "gate_owner", "gate_evidence"):
            with self.subTest(location=location):
                data = copy.deepcopy(self.data)
                if location == "decision":
                    data["answers"]["decisions"]["BD-1"]["answer"] = 1
                    diagnostic = "BD-1 lacks a complete recorded answer"
                elif location == "interim_claim":
                    data["answers"]["criteria"]["assumptions"]["answers"]["A-17"]["interim_claim"] = 1
                    diagnostic = "each assumption needs a disposition and interim Phase 4 claim"
                else:
                    field = "owner" if location == "gate_owner" else "required_evidence"
                    data["answers"]["qualification_gates"]["Q-7"][field] = 1
                    diagnostic = "physical and component qualification must remain explicit future gates, with holder and required proof"
                self.write(data)
                self.assertIn("DSR-0.6 closure: " + diagnostic, self.errors())


if __name__ == "__main__":
    unittest.main()
