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
