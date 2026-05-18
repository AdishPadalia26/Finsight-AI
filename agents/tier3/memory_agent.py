from graph.nodes import StubAgent


class MemoryAgent(StubAgent):
    """
    Agent 12 — Personalization & Memory (Tier 3, Background Async) — STUB

    Phase 2 agent. Maintains longitudinal memory of every user using a
    vector store (ChromaDB — local, free, no API key). Tracks financial progress
    over time, learns communication preferences, sends proactive check-ins.

    Requires meaningful longitudinal data across sessions.
    Architecture described in writeup. ChromaDB chosen over Pinecone —
    open source, runs in-process, cloud-safe with persistent volume.
    """

    def __init__(self):
        super().__init__(
            name="MemoryAgent",
            description=(
                "Longitudinal memory via ChromaDB vector store — tracks financial "
                "progress, learns preferences, proactive check-ins. Phase 2."
            ),
        )
