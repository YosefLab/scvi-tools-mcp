# YosefLab/scviva-tools GitHub Issues Q&A

1 issues (open and closed, bots excluded) from YosefLab/scviva-tools with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; issues are only removed once they age out of that window.

## #57: `import scviva` fails on a default install: `pooch` is not a core dependency
**Issue:** #57 | **Last activity:** 2026-10-28T08:59:37Z
**State:** closed | **Author:** @MMatinGerami | **Comments:** 1 | **Created:** 2026-10-23 | **URL:** https://github.com/YosefLab/scviva-tools/issues/57

### Bug Description

After a plain `pip install scviva-tools` (0.1.7), `import scviva` raises `ModuleNotFoundError: No module named 'pooch'`.

`scviva/__init__.py` imports `scviva.tools`, which imports `scviva.tools.harreman`, and `pooch` is imported at module level in:

- `src/scviva/tools/harreman/datasets/datasets.py:2`
- `src/scviva/tools/harreman/hotspot/local_autocorrelation.py:6`
- `src/scviva/tools/harreman/preprocessing/database.py:7`

`pooch` is only listed in the `spatial` and `file-sharing` extras. The test environments install the `spatial` extra (`envs.hatch-test.features = ["spatial"]`), so CI does not catch this.

### To Reproduce

```python
# uv run --isolated --no-project -p 3.12 --with scviva-tools==0.1.7 python -c "import scviva"
import scviva
```

```
  File ".../scviva/__init__.py", line 10, in <module>
  File ".../scviva/tools/__init__.py", line 3, in <module>
  File ".../scviva/tools/harreman/__init__.py", line 3, in <module>
  File ".../scviva/tools/harreman/datasets/__init__.py", line 1, in <module>
  File ".../scviva/tools/harreman/datasets/datasets.py", line 2, in <module>
ModuleNotFoundError: No module named 'pooch'
```

Adding `--with pooch` makes the import succeed.

### Expected Behavior

`import scviva` works after the install command in the README (`pip install scviva-tools`).

### Environment

- scviva-tools version: 0.1.7 (PyPI) and current `main` (b7e3cb2)
- Python version: 3.12.15
- scvi-tools version: 1.5.1
- OS: macOS 26 (arm64)

### Ad …

**@ori-kron-wis:** close https://github.com/YosefLab/scviva-tools/pull/60
