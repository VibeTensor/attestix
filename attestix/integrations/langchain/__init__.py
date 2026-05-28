"""LangChain integration for Attestix.

Provides :class:`AttestixCallback`, a real LangChain ``BaseCallbackHandler``
that emits a hash-chained, Ed25519-signed audit row for every LangChain
event (``on_llm_start``, ``on_tool_start``, ``on_chain_start``, ``…_end``).

Requires LangChain. Install with the opt-in extra::

    pip install 'attestix[langchain]'

Or install ``langchain-core`` directly alongside Attestix.

Importing this module without ``langchain-core`` installed raises
``ImportError`` with a clear install hint — never a confusing
``ModuleNotFoundError`` deep inside LangChain.
"""

from attestix.integrations.langchain.callback import AttestixCallback

__all__ = ["AttestixCallback"]
