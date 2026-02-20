"""Tests for services/provenance_service.py — training data, lineage, audit."""


class TestRecordTrainingData:
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


class TestRecordModelLineage:
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


class TestLogAction:
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
    def test_aggregates_all_types(self, provenance_service):
        provenance_service.record_training_data("a:1", "Dataset1")
        provenance_service.record_model_lineage("a:1", "model-v1")
        provenance_service.log_action("a:1", "inference")
        result = provenance_service.get_provenance("a:1")
        assert len(result["training_data"]) == 1
        assert len(result["model_lineage"]) == 1
        assert result["audit_log_count"] == 1


class TestAuditTrail:
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
