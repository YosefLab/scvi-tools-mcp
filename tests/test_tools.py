import asyncio


def test_recommend_model_returns_content(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import recommend_model

    result = recommend_model(
        task="batch_integration",
        data_type="scrna",
        has_protein=False,
        has_accessibility=False,
        n_batches=3,
    )
    assert result.error is None
    assert result.content is not None
    assert len(result.content) > 0


def test_get_model_overview_valid(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_overview

    result = get_model_overview(model_name="scvi")
    assert result.error is None
    assert "scvi" in result.content.lower()


def test_get_model_overview_unknown(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_overview

    result = get_model_overview(model_name="nonexistent_model")
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_get_model_parameters_valid(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_parameters

    result = get_model_parameters(model_name="scvi")
    assert result.error is None


# --- Task 8: _data_prep ---


def test_get_setup_anndata_guide_valid(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import get_setup_anndata_guide

    result = get_setup_anndata_guide(model_name="scvi")
    assert result.error is None
    assert "setup_anndata" in result.content


def test_validate_data_requirements_pass(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import validate_data_requirements

    result = validate_data_requirements(
        model_name="scvi",
        obs_keys=["batch", "cell_type"],
        var_keys=["gene_name"],
        has_raw=True,
    )
    assert result.error is None
    assert result.content is not None


def test_validate_data_requirements_missing_model(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import validate_data_requirements

    result = validate_data_requirements(
        model_name="nonexistent",
        obs_keys=[],
        var_keys=[],
        has_raw=False,
    )
    assert result.error is not None


def test_validate_data_requirements_has_raw_warning(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import validate_data_requirements

    result = validate_data_requirements(
        model_name="scanvi",
        obs_keys=["labels_key"],
        var_keys=[],
        has_raw=False,
    )
    assert result.error is None
    assert "adata.raw" in result.content
    assert "MISSING" in result.content
    assert "ACTION REQUIRED" in result.content


# --- Task 9: _tutorials ---


def test_list_tutorials_all(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import list_tutorials

    result = list_tutorials(category=None)
    assert result.error is None
    assert result.content is not None


def test_list_tutorials_category(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import list_tutorials

    result = list_tutorials(category="scrna")
    assert result.error is None


def test_get_tutorial_valid(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import get_tutorial

    result = get_tutorial(tutorial_name="scrna/harmonization", page=1)
    assert result.error is None
    assert result.content is not None


def test_get_tutorial_missing(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import get_tutorial

    result = get_tutorial(tutorial_name="scrna/nonexistent", page=1)
    assert result.error is not None


def test_search_tutorials_finds_match(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import search_tutorials

    result = search_tutorials(query="batch integration scvi")
    assert result.error is None
    assert result.content is not None


# --- Task 10: _api_reference ---


def test_get_api_reference_valid(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import get_api_reference

    result = get_api_reference(symbol="SCVI")
    assert result.error is None
    assert result.content is not None


def test_get_api_reference_unknown(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import get_api_reference

    result = get_api_reference(symbol="NonExistentClass")
    assert result.error is not None


def test_search_api_returns_results(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import search_api

    result = search_api(query="setup anndata batch")
    assert result.error is None
    assert result.content is not None


# --- Task 11: _workflows ---


def test_get_workflow_template_batch_integration(mock_knowledge):
    from scvi_tools_mcp.tools._workflows import get_workflow_template

    result = get_workflow_template(task="batch_integration", model_name="scvi")
    assert result.error is None
    assert "scvi" in result.content.lower()
    assert "```python" in result.content


def test_get_downstream_guide_de(mock_knowledge):
    from scvi_tools_mcp.tools._workflows import get_downstream_guide

    result = get_downstream_guide(model_name="scvi", task="de")
    assert result.error is None
    assert result.content is not None


# --- Task 12: _troubleshooting ---


def test_get_faq_valid_topic(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import get_faq

    result = get_faq(topic="training")
    assert result.error is None
    assert result.content is not None


def test_search_knowledge_returns_results(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge

    result = search_knowledge(query="batch integration scvi training")
    assert result.error is None
    assert result.content is not None


def test_search_knowledge_no_match(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge

    result = search_knowledge(query="xyzabcnonexistentterm12345")
    assert result.error is None
    assert result.content is not None


def test_search_knowledge_includes_hub_summary(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge

    result = search_knowledge(query="heart atlas pretrained hub")
    assert result.error is None
    assert result.content is not None
    assert "hub/summary" in result.content or "heart-cell-atlas-scvi" in result.content


def test_search_knowledge_includes_hub_model_records(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge

    result = search_knowledge(query="mdata h5mu totalvi protein")
    assert result.error is None
    assert result.content is not None
    assert "hub/models" in result.content
    assert "haniffa_covid_pbmc_totalvi" in result.content


# --- Task 13: _hub ---


def test_list_hub_models_returns_content(mock_knowledge):
    from scvi_tools_mcp.tools._hub import list_hub_models

    result = list_hub_models()
    assert result.error is None
    assert result.content is not None
    assert "human-lung-cell-atlas-scanvi" in result.content
    assert "haniffa_covid_pbmc_totalvi" in result.content


def test_list_hub_models_filters_metadata(mock_knowledge):
    from scvi_tools_mcp.tools._hub import list_hub_models

    result = list_hub_models(model_class="SCANVI", tissue="lung", annotated=True)
    assert result.error is None
    assert result.content is not None
    assert "human-lung-cell-atlas-scanvi" in result.content
    assert "heart-cell-atlas-scvi" not in result.content


def test_get_hub_model_valid(mock_knowledge):
    from scvi_tools_mcp.tools._hub import get_hub_model

    result = get_hub_model(model_id="scvi-tools/heart-cell-atlas-scvi")
    assert result.error is None
    assert result.content is not None
    assert "https://huggingface.co/scvi-tools/heart-cell-atlas-scvi" in result.content
    assert "SCVI" in result.content
    assert "heart" in result.content
    assert "load_from_hub" in result.content


def test_get_hub_model_unknown(mock_knowledge):
    from scvi_tools_mcp.tools._hub import get_hub_model

    result = get_hub_model(model_id="missing/repo")
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_suggest_hub_models_prefers_scanvi_for_label_transfer(mock_knowledge):
    from scvi_tools_mcp.tools._hub import suggest_hub_models

    result = suggest_hub_models(task="label_transfer", tissue="lung", require_annotated=True)
    assert result.error is None
    assert result.content is not None
    first_recommendation = next(line for line in result.content.splitlines() if line.startswith("1. "))
    assert "human-lung-cell-atlas-scanvi" in first_recommendation


def test_suggest_hub_models_prefers_totalvi_for_cite_seq(mock_knowledge):
    from scvi_tools_mcp.tools._hub import suggest_hub_models

    result = suggest_hub_models(task="cite_seq", modality="protein")
    assert result.error is None
    assert result.content is not None
    assert "haniffa_covid_pbmc_totalvi" in result.content


# --- Task 13: smoke test — all tools registered ---


def test_all_tools_registered():
    from scvi_tools_mcp.mcp import mcp

    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    expected = {
        "recommend_model",
        "get_model_overview",
        "get_model_parameters",
        "get_setup_anndata_guide",
        "validate_data_requirements",
        "list_tutorials",
        "get_tutorial",
        "search_tutorials",
        "get_api_reference",
        "search_api",
        "get_workflow_template",
        "get_downstream_guide",
        "get_faq",
        "search_knowledge",
        "list_hub_models",
        "get_hub_model",
        "suggest_hub_models",
    }
    assert expected == names, f"Missing: {expected - names}, Extra: {names - expected}"
