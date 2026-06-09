# tests/test_tools.py
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
