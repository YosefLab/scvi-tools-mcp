---
name: Release checklist
about: Checklist for maintainers
title: ""
labels: releases
assignees: ""
---

- [ ] Bump version in `src/scvi_tools_mcp/__init__.py`
- [ ] Update `CHANGELOG.md` — move `[Unreleased]` entries under the new version heading
- [ ] Run knowledge refresh scripts and verify diffs look correct:
    - `python scripts/scrape_external.py`
    - `python scripts/extract_api_docs.py`
    - `python scripts/convert_notebooks.py --src /path/to/scvi-tutorials --dst src/scvi_tools_mcp/knowledge/tutorials`
- [ ] Run the full test suite: `pytest`
- [ ] Create and push the version tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Verify the `release.yaml` workflow completes and the package appears on [PyPI](https://pypi.org/project/scvi-tools-mcp/)
- [ ] Update the `claude mcp add` command in README if the interface changed
