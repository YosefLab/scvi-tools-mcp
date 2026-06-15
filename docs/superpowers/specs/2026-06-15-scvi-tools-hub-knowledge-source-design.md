# scvi-tools Hugging Face Hub Knowledge Source - Design Spec

**Date:** 2026-06-15
**Status:** Approved for implementation planning
**Author:** ori-kron-wis

---

## 1. Overview

Add the official [scvi-tools Hugging Face organization](https://huggingface.co/scvi-tools) as a first-class knowledge source for `scvi-tools-mcp`. The source captures the public pretrained model registry exposed by Hugging Face and makes it available to MCP clients without runtime network access.

The hub snapshot answers a different class of questions from the existing model documentation:

- Which pretrained scvi-tools HubModels exist?
- Which model class, modality, tissue, and annotation status does each repo represent?
- Which repos are suitable starting points for transfer learning, label transfer, reference mapping, CITE-seq, deconvolution, or example code?
- Which Hugging Face repo should a user inspect or download next?

---

## 2. Goals

- Add a bundled Hugging Face Hub snapshot under `src/scvi_tools_mcp/knowledge/hub/`.
- Refresh that snapshot once every three months through GitHub Actions.
- Expose dedicated MCP tools for listing, inspecting, and suggesting hub models.
- Include the hub snapshot in broad `search_knowledge` results.
- Update architecture, public docs, README, and changelog so the source is visible and maintainable.
- Keep the existing invariant: no network calls during MCP tool execution.

---

## 3. Non-goals

- Downloading `model.pt`, `adata.h5ad`, `mdata.h5mu`, or other large Hugging Face artifacts.
- Loading, training, validating, or executing any pretrained model.
- Mirroring model cards in full.
- Adding Hugging Face authentication to runtime tools.
- Auto-choosing models based on biological correctness beyond metadata tags and documented intended use.

---

## 4. Source Shape

The source is the Hugging Face model API for the `scvi-tools` author:

```text
https://huggingface.co/api/models?author=scvi-tools&full=false&sort=lastModified&direction=-1&limit=200
```

The current snapshot, checked on 2026-06-15, contains 121 public repos. Useful metadata fields include:

- `modelId`
- `lastModified`
- `createdAt`
- `downloads`
- `likes`
- `tags`
- `library_name`
- `siblings`

The `tags` list carries the most important scvi-tools metadata:

- `model_cls_name:<class>` such as `SCVI`, `SCANVI`, `TOTALVI`, `CondSCVI`, or `RNAStereoscope`
- `scvi_version:<version>`
- `anndata_version:<version>`
- `modality:<name>` such as `rna` or `protein`
- `tissue:<name>`
- `annotated:<True|False>`
- `license:<id>`

---

## 5. Approaches Considered

### A. Search-only Markdown Snapshot

Store one Markdown file listing all hub repos and let `search_knowledge` discover it.

**Pros:** Smallest change, no new tool surface.
**Cons:** Weak for agents. Filtering by class, modality, tissue, or annotation status becomes brittle text search.

### B. Dedicated Tools + Bundled Snapshot

Store a normalized JSON snapshot plus a Markdown summary, then add dedicated MCP tools:

- `list_hub_models`
- `get_hub_model`
- `suggest_hub_models`

**Pros:** Agents can reliably filter and explain hub choices. Runtime stays offline. Search still works.
**Cons:** Adds one tool module, more tests, and one quarterly workflow.

### C. Live Hugging Face Lookup at Tool Time

Call Hugging Face directly from the MCP tools.

**Pros:** Always current.
**Cons:** Violates the package's offline-runtime design, introduces network failure modes, and may leak user intent through third-party calls.

**Decision:** Use approach B. It best matches the existing architecture and gives LLM clients a dependable API for hub recommendations.

---

## 6. Architecture

### 6.1 Knowledge Files

Add:

```text
src/scvi_tools_mcp/knowledge/hub/
├── models.json
└── summary.md
```

`models.json` stores normalized records:

```json
{
  "fetched_at": "2026-06-15T00:00:00Z",
  "source_url": "https://huggingface.co/scvi-tools",
  "api_url": "https://huggingface.co/api/models?author=scvi-tools&full=false&sort=lastModified&direction=-1&limit=200",
  "models": [
    {
      "model_id": "scvi-tools/heart-cell-atlas-scvi",
      "url": "https://huggingface.co/scvi-tools/heart-cell-atlas-scvi",
      "model_class": "SCVI",
      "modalities": ["rna"],
      "tissues": ["heart"],
      "annotated": true,
      "scvi_version": "1.4.2",
      "anndata_version": "0.12.7",
      "license": "cc-by-4.0",
      "downloads": 0,
      "likes": 1,
      "last_modified": "2026-03-01T10:58:11.000Z",
      "files": ["README.md", "_scvi_required_metadata.json", "adata.h5ad", "metrics.json", "model.pt"]
    }
  ]
}
```

`summary.md` stores a human-readable registry overview:

- total repo count
- counts by model class
- counts by modality
- counts by annotation status
- top recently modified repos
- notes on how to use HubModel repos from scvi-tools

### 6.2 Scraper

Add `scripts/scrape_huggingface_hub.py`.

Responsibilities:

- Fetch the Hugging Face API response.
- Normalize tag-derived metadata into explicit fields.
- Sort repos by `last_modified` descending.
- Write `knowledge/hub/models.json`.
- Write `knowledge/hub/summary.md`.
- Avoid downloading large sibling files.
- Fail loudly on malformed API responses so CI does not silently publish a bad snapshot.

### 6.3 Quarterly Refresh

Add `.github/workflows/sync_huggingface_hub.yaml`.

Schedule:

```yaml
on:
  schedule:
    - cron: "0 6 1 */3 *"
  workflow_dispatch:
```

The workflow installs dev dependencies, runs `python scripts/scrape_huggingface_hub.py`, checks `src/scvi_tools_mcp/knowledge/hub/` for diffs, and opens an automated PR titled `chore: sync scvi-tools Hugging Face hub snapshot`.

### 6.4 Tool Module

Add `src/scvi_tools_mcp/tools/_hub.py` and import it from `mcp.py`.

Tool result model:

```python
class HubResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None
```

Tool API:

```python
list_hub_models(
    model_class: str | None = None,
    modality: str | None = None,
    tissue: str | None = None,
    annotated: bool | None = None,
    page: int = 1,
    page_size: int = 25,
) -> HubResult
```

Returns a paginated table of repo IDs, model class, modalities, tissues, annotation status, version, and URL.

```python
get_hub_model(model_id: str) -> HubResult
```

Returns one normalized repo record plus usage guidance and a Hugging Face URL.

```python
suggest_hub_models(
    task: Literal[
        "reference_mapping",
        "label_transfer",
        "query_embedding",
        "cite_seq",
        "spatial_deconvolution",
        "example_usage",
    ],
    modality: str | None = None,
    tissue: str | None = None,
    require_annotated: bool = False,
    limit: int = 5,
) -> HubResult
```

Ranks hub repos by simple metadata rules:

- `label_transfer` and `reference_mapping`: prefer annotated `SCANVI` then annotated `SCVI`.
- `query_embedding`: prefer `SCVI` and matching tissue/modality.
- `cite_seq`: prefer `TOTALVI` with `protein` modality.
- `spatial_deconvolution`: prefer `RNAStereoscope` and `CondSCVI` pairs.
- `example_usage`: include recent small/test repos but label them as examples, not biological references.

---

## 7. Search Integration

Update `search_knowledge` so it searches `knowledge/hub/summary.md` and, if practical, selected model records from `models.json`.

The search result should label matches with `hub` so users can distinguish pretrained model registry results from model docs, tutorials, API references, and FAQ content.

---

## 8. Documentation Updates

Update:

- `README.md`: add hub tools, hub source directory, and quarterly workflow.
- `docs/index.md`: mention Hub as a supported knowledge source.
- `docs/architecture/index.md`: update tool-module count, knowledge source list, and refresh pipeline.
- `docs/architecture/scvi-tools-mcp-block-diagram.html`: add Hub tool module, `knowledge/hub/`, scraper, and quarterly workflow notes.
- `CHANGELOG.md`: add an Unreleased entry for HF Hub knowledge source and tools.
- Existing design/spec docs: add a short addendum or this standalone spec reference so future architecture work sees the hub design.

---

## 9. Testing Strategy

Tests use local fixture knowledge, not network calls.

Add fixture files:

```text
tests/fixtures/knowledge/hub/
├── models.json
└── summary.md
```

Add tests:

- `list_hub_models` returns paginated content for all fixture models.
- `list_hub_models` filters by model class, modality, tissue, and annotation flag.
- `get_hub_model` returns details for a known repo.
- `get_hub_model` returns an error for an unknown repo.
- `suggest_hub_models` prefers annotated `SCANVI` for label transfer.
- `suggest_hub_models` prefers `TOTALVI` for CITE-seq.
- tool registration includes the three new hub tools.
- scraper normalization parses Hugging Face tags into explicit metadata fields.
- scraper summary includes model class and modality counts.

---

## 10. Error Handling

- Missing `knowledge/hub/models.json`: return an error asking maintainers to run `scripts/scrape_huggingface_hub.py`.
- Unknown model ID: return an error with a few available repo IDs.
- Empty filter result: return an empty-result message, not an exception.
- Malformed snapshot: return an error from tools and fail scraper tests.
- Large result sets: paginate instead of truncating mid-record.

---

## 11. Security and Privacy

- MCP tools only read bundled files.
- The scraper only calls the Hugging Face public API during local/CI refresh.
- The scraper does not download model weights, AnnData, MuData, TensorBoard logs, or metadata sidecar files.
- Runtime tools expose Hugging Face URLs but do not fetch them.

---

## 12. Implementation Order

1. Add failing tests for hub tools and scraper normalization.
2. Add fixture hub snapshot.
3. Implement `scripts/scrape_huggingface_hub.py`.
4. Generate the initial `knowledge/hub/` snapshot.
5. Implement `_hub.py` and register it in `mcp.py`.
6. Include hub snapshot in `search_knowledge`.
7. Add quarterly GitHub Actions workflow.
8. Update README, architecture docs, block diagram, and changelog.
9. Run formatting and test suite.

---

## 13. Open Questions

None. User approved dedicated hub tools plus bundled searchable knowledge on 2026-06-15.
