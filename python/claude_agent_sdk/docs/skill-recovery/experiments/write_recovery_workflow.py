"""Disposable Phase 1 fixed effect proof; no general effect executor is registered."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn
class WriteRecoveryProof:
    """Commit the deferred segment before dispatch and retain its recorded outcome."""

    def __init__(self):
        self.stage = "starting"
        self.accepted = None
        self.outcome = None
        self.dispatch = False
        self.replace = False

    @workflow.query
    def state(self):
        return {"stage": self.stage, "accepted": self.accepted, "outcome": self.outcome}

    @workflow.signal
    def allow_dispatch(self):
        self.dispatch = True

    @workflow.signal
    def allow_recovery(self):
        self.replace = True

    @workflow.run
    async def run(self, session: str):
        self.accepted = await workflow.execute_activity(
            "proof_segment",
            session,
            start_to_close_timeout=timedelta(seconds=65),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
        self.stage = "segment_committed"
        await workflow.wait_condition(lambda: self.dispatch)
        self.outcome = await workflow.execute_activity(
            "proof_write",
            self.accepted,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
        if self.outcome.get("parked"):
            self.stage = "parked"
            await workflow.wait_condition(lambda: False)
        self.stage = "effect_committed"
        await workflow.wait_condition(lambda: self.replace)
        result = await workflow.execute_activity(
            "proof_recovery",
            {"accepted": self.accepted, "outcome": self.outcome},
            start_to_close_timeout=timedelta(seconds=65),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
        self.stage = "finished"
        return result
