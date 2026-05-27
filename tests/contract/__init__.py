"""Contract test suites for the v0.4.0 extensibility seams.

Each suite is parametrized over every concrete implementation of a seam
(Repository, Signer) so the default and any alternative adapter must satisfy the
identical contract — enforcing Liskov substitution at the boundary
(constitution principle III).
"""
