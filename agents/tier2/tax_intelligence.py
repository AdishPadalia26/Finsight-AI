from graph.nodes import StubAgent


class TaxIntelligenceAgent(StubAgent):
    """
    Agent 07 — Tax Intelligence (Tier 2, Parallel) — STUB

    Phase 2 agent. Year-round tax planning: tax-loss harvesting windows,
    Roth conversion opportunities, HSA maximization, 2025 IRS contribution limits.
    Calculates exact dollar impact of each tax move.

    IRS API access requires complex integration. 2025 contribution limits
    (401k: $23,500 / IRA: $7,000 / HSA: $4,300) hardcoded in writeup.
    Stubbed here.
    """

    def __init__(self):
        super().__init__(
            name="TaxIntelligenceAgent",
            description=(
                "Year-round tax optimization: harvesting windows, Roth conversions, "
                "HSA maximization, 2025 IRS limits. Phase 2."
            ),
        )
