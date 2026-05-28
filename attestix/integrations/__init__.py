"""Attestix framework integrations.

This subpackage ships the callback/adapter classes that let popular agent
frameworks log every step to the Attestix audit chain.

Available integrations (importable lazily — each requires its framework as
an opt-in extra):

- ``attestix.integrations.langchain`` — ``AttestixCallback`` (LangChain
  ``BaseCallbackHandler``). Install: ``pip install 'attestix[langchain]'``.
- ``attestix.integrations.openai_agents`` — ``AttestixAuditHook`` (helper for
  the OpenAI Agents SDK). Install: ``pip install 'attestix[openai-agents]'``.
- ``attestix.integrations.crewai`` — ``AttestixCrewAdapter`` (helper for
  CrewAI). Install: ``pip install 'attestix[crewai]'``.

The integration modules import their respective framework lazily so that
``import attestix.integrations`` alone never requires the framework to be
installed.
"""

__all__ = ["langchain", "openai_agents", "crewai"]
