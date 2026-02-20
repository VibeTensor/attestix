"""Tests for services/reputation_service.py — trust scoring."""


class TestRecordInteraction:
    def test_records_and_returns_score(self, reputation_service):
        result = reputation_service.record_interaction(
            agent_id="attestix:bot1",
            counterparty_id="attestix:bot2",
            outcome="success",
        )
        assert result["recorded"] is True
        assert result["updated_score"]["trust_score"] > 0

    def test_invalid_outcome(self, reputation_service):
        result = reputation_service.record_interaction(
            agent_id="attestix:bot1",
            counterparty_id="attestix:bot2",
            outcome="invalid_outcome",
        )
        assert "error" in result

    def test_success_higher_than_failure(self, reputation_service):
        reputation_service.record_interaction("a:1", "a:2", "success")
        score_success = reputation_service.get_reputation("a:1")["trust_score"]

        reputation_service.record_interaction("a:3", "a:4", "failure")
        score_failure = reputation_service.get_reputation("a:3")["trust_score"]

        assert score_success > score_failure


class TestGetReputation:
    def test_no_interactions(self, reputation_service):
        result = reputation_service.get_reputation("attestix:unknown")
        assert result["trust_score"] is None
        assert result["total_interactions"] == 0

    def test_category_breakdown(self, reputation_service):
        reputation_service.record_interaction("a:1", "a:2", "success", category="task")
        reputation_service.record_interaction("a:1", "a:3", "failure", category="delegation")
        result = reputation_service.get_reputation("a:1")
        assert "task" in result["category_breakdown"]
        assert "delegation" in result["category_breakdown"]
        assert result["category_breakdown"]["task"]["success"] == 1
        assert result["category_breakdown"]["delegation"]["failure"] == 1


class TestQueryReputation:
    def test_filter_by_min_score(self, reputation_service):
        reputation_service.record_interaction("a:good", "a:x", "success")
        reputation_service.record_interaction("a:bad", "a:x", "failure")
        results = reputation_service.query_reputation(min_score=0.5)
        agent_ids = [r["agent_id"] for r in results]
        assert "a:good" in agent_ids
        assert "a:bad" not in agent_ids

    def test_filter_by_min_interactions(self, reputation_service):
        reputation_service.record_interaction("a:1", "a:x", "success")
        reputation_service.record_interaction("a:1", "a:x", "success")
        reputation_service.record_interaction("a:2", "a:x", "success")
        results = reputation_service.query_reputation(min_interactions=2)
        assert len(results) == 1
        assert results[0]["agent_id"] == "a:1"
