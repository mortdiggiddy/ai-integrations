"""Disposable signed approval Workflow for the bounded recovery comparison."""

import hashlib
import json

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    from tests.hybrid.models import State
    from tests.hybrid.workflows import HybridWorkflow


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def request_digest(session, call):
    return hashlib.sha256(
        canonical(
            {
                "session": session,
                "id": call.id,
                "name": call.name,
                "input": call.arguments,
                "transcript_uuid": call.transcript_uuid,
                "subpath": call.subpath,
            }
        )
    ).hexdigest()


@workflow.defn
class SignedApprovalWorkflow(HybridWorkflow):
    def __init__(self):
        super().__init__()
        self.public_key = ""
        self.decisions = {}
        self.completed = False
        self.finish_requested = False

    @workflow.run
    async def run(self, inp: dict) -> State:
        self.public_key = inp["public_key"]
        result = await self.drive(State(inp["session"], ["work"]))
        self.completed = True
        await workflow.wait_condition(lambda: self.finish_requested)
        await workflow.wait_condition(workflow.all_handlers_finished)
        return result

    def validate_token(self, token):
        if not isinstance(token, dict) or set(token) != {"body", "signature"}:
            raise ValueError("unsigned or malformed decision")
        body = token["body"]
        if set(body) != {
            "version",
            "key_id",
            "workflow",
            "session",
            "id",
            "digest",
            "approved",
            "expires",
        }:
            raise ValueError("invalid decision fields")
        if body["version"] != 1 or body["key_id"] != "experiment-key":
            raise ValueError("unsupported signing identity")
        if type(body["approved"]) is not bool or type(body["expires"]) is not int:
            raise ValueError("invalid decision types")
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.public_key)).verify(
            bytes.fromhex(token["signature"]), canonical(body)
        )
        if body["expires"] <= workflow.now().timestamp():
            raise ValueError("expired decision")
        entry = self.state.ledger.get(body["id"])
        if entry is None or not entry.call.arguments.get("approval"):
            raise ValueError("unknown accepted request")
        if (
            body["workflow"] != workflow.info().workflow_id
            or body["session"] != self.state.session_id
            or body["digest"] != request_digest(self.state.session_id, entry.call)
        ):
            raise ValueError("decision does not bind accepted request")
        previous = self.decisions.get(body["id"])
        if previous is not None and previous != body["approved"]:
            raise ValueError("conflicting signed decision")

    @workflow.update
    async def review(self, token: dict) -> None:
        self.validate_token(token)
        body = token["body"]
        self.decisions[body["id"]] = body["approved"]
        self.state.ledger[body["id"]].approved = body["approved"]

    @review.validator
    def validate_review(self, token: dict) -> None:
        self.validate_token(token)

    @workflow.query
    def signed_state(self) -> dict:
        return {"decisions": self.decisions, "completed": self.completed}

    @workflow.update
    async def finish_experiment(self) -> None:
        self.finish_requested = True
