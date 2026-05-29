"""Tests for training data, lineage, and audit in services/provenance_service.py."""


class TestRecordTrainingData:
    """Tests for recording training data provenance entries."""

    def test_records_entry(self, provenance_service):
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1",
            dataset_name="WikiText-103",
            source_url="https://huggingface.co/datasets/wikitext",
            license="CC BY-SA 3.0",
            data_categories=["text"],
        )
        assert result["entry_id"].startswith("prov:")
        assert result["entry_type"] == "training_data"
        assert result["dataset_name"] == "WikiText-103"
        assert result["signature"] is not None

    def test_personal_data_flag(self, provenance_service):
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1",
            dataset_name="UserFeedback",
            contains_personal_data=True,
        )
        assert result["contains_personal_data"] is True

    def test_dataset_version_stored(self, provenance_service):
        # Issue #39: dataset_version is a first-class param now.
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1",
            dataset_name="SafetyBench",
            dataset_version="2.0.1",
        )
        assert result["dataset_version"] == "2.0.1"

    def test_source_alias_resolves_to_source_url(self, provenance_service):
        # Issue #39 repro: source= must work without TypeError and land in
        # the canonical source_url field.
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1",
            dataset_name="SafetyBench",
            dataset_version="2.0.1",
            source="https://huggingface.co/datasets/safetybench",
            license="CC-BY-4.0",
        )
        assert "error" not in result
        assert result["source_url"] == "https://huggingface.co/datasets/safetybench"

    def test_source_url_wins_over_source_alias(self, provenance_service):
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1",
            dataset_name="SafetyBench",
            source_url="https://canonical.example/ds",
            source="https://alias.example/ds",
        )
        assert result["source_url"] == "https://canonical.example/ds"

    def test_issue_39_repro_does_not_raise(self, provenance_service):
        # Exact form from issue #39.
        result = provenance_service.record_training_data(
            agent_id="attestix:bot1", dataset_name="SafetyBench",
            dataset_version="2.0.1",
            source="https://huggingface.co/...", license="CC-BY-4.0",
        )
        assert result["entry_type"] == "training_data"


class TestRecordModelLineage:
    """Tests for recording model lineage and fine-tuning metadata."""

    def test_records_lineage(self, provenance_service):
        result = provenance_service.record_model_lineage(
            agent_id="attestix:bot1",
            base_model="gpt-4",
            base_model_provider="OpenAI",
            fine_tuning_method="LoRA",
            evaluation_metrics={"accuracy": 0.95},
        )
        assert result["entry_type"] == "model_lineage"
        assert result["base_model"] == "gpt-4"
        assert result["evaluation_metrics"]["accuracy"] == 0.95

    def test_training_config_stored(self, provenance_service):
        # Issue #39 repro: training_config= must work without TypeError and
        # land in the entry alongside evaluation_metrics.
        result = provenance_service.record_model_lineage(
            agent_id="attestix:bot1", base_model="gpt-4",
            fine_tuning_method="LoRA",
            training_config={"epochs": 3, "lr": 1e-5},
        )
        assert "error" not in result
        assert result["training_config"] == {"epochs": 3, "lr": 1e-5}

    def test_training_config_and_metrics_coexist(self, provenance_service):
        result = provenance_service.record_model_lineage(
            agent_id="attestix:bot1", base_model="gpt-4",
            evaluation_metrics={"accuracy": 0.9},
            training_config={"epochs": 5},
        )
        assert result["evaluation_metrics"]["accuracy"] == 0.9
        assert result["training_config"]["epochs"] == 5


class TestLogAction:
    """Tests for logging agent actions to the audit trail."""

    def test_logs_action(self, provenance_service):
        result = provenance_service.log_action(
            agent_id="attestix:bot1",
            action_type="inference",
            input_summary="User query",
            output_summary="AI response",
        )
        assert result["log_id"].startswith("audit:")
        assert result["action_type"] == "inference"

    def test_invalid_action_type(self, provenance_service):
        result = provenance_service.log_action(
            agent_id="attestix:bot1",
            action_type="invalid_type",
        )
        assert "error" in result

    def test_human_override_flag(self, provenance_service):
        result = provenance_service.log_action(
            agent_id="attestix:bot1",
            action_type="inference",
            human_override=True,
        )
        assert result["human_override"] is True


class TestGetProvenance:
    """Tests for aggregating provenance records across all entry types."""

    def test_aggregates_all_types(self, provenance_service):
        provenance_service.record_training_data("a:1", "Dataset1")
        provenance_service.record_model_lineage("a:1", "model-v1")
        provenance_service.log_action("a:1", "inference")
        result = provenance_service.get_provenance("a:1")
        assert len(result["training_data"]) == 1
        assert len(result["model_lineage"]) == 1
        # v0.4.0-rc.3 (P0 #5): audit_log_count now aggregates the legacy
        # `provenance.json::audit_log` chain (written by log_action — 1 row
        # here) AND the new `audit.json::events` chain (written by every
        # state-changing service via safe_emit — 3 more rows here, one each
        # for record_training_data / record_model_lineage / log_action). The
        # individual sub-counts are exposed for callers that want to keep
        # the original semantics.
        assert result["audit_log_count"] >= 1
        assert result["audit_chain_count_legacy"] == 1
        assert result["audit_events_count"] >= 3


class TestAuditTrail:
    """Tests for querying and filtering the audit trail."""

    def test_filters_by_action_type(self, provenance_service):
        provenance_service.log_action("a:1", "inference")
        provenance_service.log_action("a:1", "delegation")
        provenance_service.log_action("a:1", "inference")
        results = provenance_service.get_audit_trail("a:1", action_type="inference")
        assert len(results) == 2

    def test_filters_by_agent(self, provenance_service):
        provenance_service.log_action("a:1", "inference")
        provenance_service.log_action("a:2", "inference")
        results = provenance_service.get_audit_trail("a:1")
        assert len(results) == 1

    def test_limit(self, provenance_service):
        for _ in range(10):
            provenance_service.log_action("a:1", "inference")
        results = provenance_service.get_audit_trail("a:1", limit=3)
        assert len(results) == 3
