"""Real SDK dispatch with local functions and temporary Attestix storage only."""

import pytest

pytest.importorskip("langchain_core")

from langchain_core.callbacks import CallbackManager
from langchain_core.outputs import Generation, LLMResult
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import StructuredTool

from attestix.integrations.langchain import AttestixCallback
from attestix.services.credential_service import CredentialService


@pytest.fixture
def callback(tmp_attestix):
    handler = AttestixCallback(display_name="Offline SDK fixture")
    # SDK managers must propagate callback failures instead of hiding a regression.
    handler.raise_error = True
    return handler


def test_runnable_dispatch_logs_chain_and_issues_verified_credential(callback):
    result = RunnableLambda(lambda value: {"echo": value}).invoke(
        "synthetic input", config={"callbacks": [callback]},
    )

    assert result == {"echo": "synthetic input"}
    summary = callback.get_audit_summary()
    assert summary["event_count"] == 1
    assert summary["audit_entries"] == 2
    assert summary["trail"][1]["prev_hash"] == summary["trail"][0]["chain_hash"]
    credentials = CredentialService().list_credentials(
        agent_id=callback.agent_id, credential_type="ChainExecutionCredential",
    )
    assert len(credentials) == 1
    assert CredentialService().verify_credential(credentials[0]["id"])["valid"]


def test_nested_runnables_accept_parent_runs_and_none_serialization(callback):
    pipeline = RunnableLambda(lambda value: value + 1) | RunnableLambda(lambda value: value * 2)

    assert pipeline.invoke(2, config={"callbacks": [callback]}) == 6
    summary = callback.get_audit_summary()
    assert summary["event_count"] == 3
    assert summary["audit_entries"] == 6
    assert all(entry["signature"] for entry in summary["trail"])


def test_public_structured_tool_invocation_emits_real_tool_callbacks(callback):
    def echo(value: str) -> str:
        """Return a synthetic fixture string locally."""
        return value

    tool = StructuredTool.from_function(echo)
    result = tool.invoke({"value": "offline tool"}, config={"callbacks": [callback]})

    assert result == "offline tool"
    summary = callback.get_audit_summary()
    assert summary["event_count"] == 1
    assert summary["audit_entries"] == 2
    assert all(entry["action_type"] == "external_call" for entry in summary["trail"])


def test_callback_manager_handles_constructed_llm_result_without_a_provider(callback):
    manager = CallbackManager([callback])
    run = manager.on_llm_start({"id": ["synthetic", "fixture"]}, ["offline prompt"])[0]
    run.on_llm_end(LLMResult(
        generations=[[Generation(text="offline response")]],
        llm_output={"token_usage": {"total_tokens": 7}},
    ))

    summary = callback.get_audit_summary()
    assert summary["audit_entries"] == 2
    assert "7 tokens" in summary["trail"][-1]["output_summary"]


def test_failed_runnable_never_issues_a_success_credential(callback):
    def fail(_value):
        raise ValueError("synthetic local failure")

    with pytest.raises(ValueError, match="synthetic local failure"):
        RunnableLambda(fail).invoke(None, config={"callbacks": [callback]})

    assert CredentialService().list_credentials(
        agent_id=callback.agent_id, credential_type="ChainExecutionCredential",
    ) == []
