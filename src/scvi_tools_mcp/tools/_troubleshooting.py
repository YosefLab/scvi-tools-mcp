from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils

FAQ_CONTENT: dict[str, str] = {
    "training": """# Training FAQ

## Loss is not decreasing
- Check adata.X contains **raw counts** (not log-normalized).
- Try `early_stopping=True`.
- Reduce `n_latent` if dataset is small (<5000 cells).
- Lower learning rate: `plan_kwargs={"lr": 1e-3}`.

## Training is slow
- Ensure GPU: `scvi.settings.dl_num_workers = 4`.
- Use `batch_size=512` for large datasets.

## CUDA out of memory
- Reduce `batch_size` (default 128).
- Reduce `n_hidden` or `n_layers`.
""",
    "data_setup": """# Data Setup FAQ

## ValueError: adata.X does not contain count data
- scVI requires raw integer counts. Reload raw data or use `layer='counts'`.

## KeyError: batch_key not found
- Check: `print(adata.obs.columns.tolist())`.

## setup_anndata must be called before model instantiation
- Always call `ModelClass.setup_anndata(adata, ...)` before `model = ModelClass(adata)`.
""",
    "gpu": """# GPU FAQ

## Check GPU availability
```python
import torch
print(torch.cuda.is_available())
```

## Force CPU training
```python
model.train(accelerator="cpu")
```
""",
    "saving_loading": """# Saving and Loading Models

## Save
```python
model.save("my_model_dir/", overwrite=True)
```

## Load
```python
model = scvi.model.SCVI.load("my_model_dir/", adata=adata)
```

## HuggingFace Hub
```python
model = scvi.model.SCVI.load_from_hub("username/model-name")
```
""",
    "convergence": """# Convergence FAQ

## Check if training converged
```python
import matplotlib.pyplot as plt
plt.plot(model.history["elbo_train"], label="train")
plt.plot(model.history["elbo_validation"], label="val")
plt.legend()
```

## Validation loss diverges
- Increase `train_size` (default 0.9).
- Use `early_stopping=True`.

## NaN loss
- Lower lr: `plan_kwargs={"lr": 5e-4}`.
- Clip gradients: `plan_kwargs={"gradient_clip_val": 1.0}`.
""",
    "batch_correction": """# Batch Correction FAQ

## Which model?
- scVI: standard scRNA-seq
- SCANVI: when you have cell type labels
- SysVI: very strong batch effect (cross-species)
- MultiVI: ATAC + RNA

## How many latent dims?
Default 30. Try 10–50.

## Evaluate batch correction
```python
import scib
metrics = scib.metrics.metrics(adata, adata_int, batch_key="batch",
                                label_key="cell_type", embed="X_scVI")
```
""",
    "memory": """# Memory FAQ

## Dataset too large for RAM
```python
adata = anndata.read_h5ad("file.h5ad", backed='r')
```

## Reduce memory during training
- Reduce `batch_size`.
- Use `precision="16-mixed"`: `model.train(precision="16-mixed")`.
""",
}


class TroubleshootResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


@mcp.tool()
def get_faq(
    topic: Literal["training", "data_setup", "gpu", "saving_loading", "convergence", "batch_correction", "memory"],
) -> TroubleshootResult:
    """Get curated FAQ entries for common scvi-tools problems.

    Combines knowledge from official docs, GitHub issues, and Discourse threads.
    Use this when a user reports an error or asks 'why is X not working'.

    Args:
        topic: The problem area. Options: training, data_setup, gpu, saving_loading,
               convergence, batch_correction, memory.
    """
    try:
        content = FAQ_CONTENT.get(topic, "")
        knowledge_dir = utils.get_knowledge_dir()
        faq_dir = knowledge_dir / "faq"
        extras: list[str] = []
        if faq_dir.exists():
            for faq_file in sorted(faq_dir.glob("*.md")):
                text = faq_file.read_text(encoding="utf-8")
                if topic.lower() in text.lower() or topic.replace("_", " ") in text.lower():
                    for i, line in enumerate(text.splitlines()):
                        if topic.replace("_", " ") in line.lower() or topic in line.lower():
                            chunk = "\n".join(text.splitlines()[max(0, i - 1) : i + 5])
                            extras.append(chunk)
                            break
        if extras:
            content += "\n\n---\n\n## From Community\n\n" + "\n\n".join(extras[:3])
        if not content:
            return TroubleshootResult(error=f"No FAQ content for topic '{topic}'.")
        result = utils.truncate(content)
        return TroubleshootResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TroubleshootResult(error=str(e))


@mcp.tool()
def search_knowledge(query: str) -> TroubleshootResult:
    """Search all scvi-tools knowledge: models, tutorials, user guide, API, and community FAQ.

    Use this tool when no other tool exactly matches the user's question. Searches
    across all knowledge sources and returns ranked excerpts. Good for: 'how do I do X',
    'what is the difference between X and Y', 'I got error Z'.

    Args:
        query: Free-text question or keywords (e.g. 'how to save a model', 'ELBO explanation').
    """
    try:
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        if not keywords:
            return TroubleshootResult(error="Query too short. Please provide at least one keyword.")
        knowledge_dir = utils.get_knowledge_dir()
        results: list[tuple[int, str, str]] = []
        for md in sorted(knowledge_dir.rglob("*.md")):
            if ".gitkeep" in md.name:
                continue
            try:
                content = md.read_text(encoding="utf-8")
            except Exception:
                continue
            score = sum(content.lower().count(kw) for kw in keywords)
            if score > 0:
                excerpt = next(
                    (
                        line.strip()[:150]
                        for line in content.splitlines()
                        if any(kw in line.lower() for kw in keywords) and len(line.strip()) > 20
                    ),
                    "",
                )
                rel = str(md.relative_to(knowledge_dir).with_suffix(""))
                results.append((score, rel, excerpt))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# Knowledge Search: '{query}'", ""]
        for _, name, excerpt in results[:8]:
            lines.append(f"- **{name}**")
            if excerpt:
                lines.append(f"  > {excerpt}")
        if not results:
            lines += [
                "No results found.",
                "",
                "Suggestions:",
                "- Try broader keywords",
                "- Use list_tutorials() to browse tutorials",
                "- Use recommend_model() for model selection",
                "- Use get_faq() for common troubleshooting",
            ]
        result = utils.truncate("\n".join(lines))
        return TroubleshootResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TroubleshootResult(error=str(e))
