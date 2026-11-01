# YosefLab/scviva-tools GitHub Pull Requests

39 pull requests (open, closed and merged, bots excluded) from YosefLab/scviva-tools with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; PRs are only removed once they age out of that window.

## #58: fix(deps): add pooch to core dependencies
**PR:** #58 | **Last activity:** 2026-10-29T02:27:11Z
**State:** closed | **Author:** @MMatinGerami | **Comments:** 1 | **Created:** 2026-10-23 | **URL:** https://github.com/YosefLab/scviva-tools/pull/58

## Description

Fixes #57. `pooch` is imported at module level by `scviva.tools.harreman`, which `import scviva` loads, but it was only listed in the `spatial` and `file-sharing` extras. A plain `pip install scviva-tools` therefore failed on `import scviva`. This adds `pooch` to the core `dependencies` and a CHANGELOG entry. The extras are left unchanged.

## Type of Change

- [x] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [x] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

Checks run on this branch:

- Built the wheel (`uv build --wheel`). Its metadata now has an unconditional `Requires-Dist: pooch`.
- Installed only that wheel in clean isolated environments (no extras, `squidpy` absent): `import scviva` succeeds on Python 3.12.15 and 3.13.14. The 0.1.7 release fails the same check with `ModuleNotFoundError: No module named 'pooch'`.
- `pytest tests/model tests/base tests/utils tests/external tests/tools tests/plotting` (excluding `test_diagvi.py`, which needs `torch-geometric`): 214 passed, 17 skipped.
- `pre-commit run` on the changed files passes.

No new test: the hatch test environments install the `spatial` extra, so a test there cannot see a missing core dependency.

## Checklist

- [x] Code follows project style (`ruff check src/ tests/`)
- [x] Documentation updated if needed
- [x] CHANGELOG.md updated

**@ori-kron-wis:** @MMatinGerami Thanks for noticing. Our solution is to use decorators, as pooch is used for file sharing, which is not a core requirement, and we want to keep the installation light. I added your name on the commit message (we are not thanking users from the community on the changlog itself).
I will have it fixed in a different PR: https://github.com/YosefLab/scviva-tools/pull/60.

Closing here.

## #64: release: v0.1.8
**PR:** #64 | **Last activity:** 2026-10-28T09:53:40Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-10-28 | **URL:** https://github.com/YosefLab/scviva-tools/pull/64

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #61: docs: expand installation guide, add Google Colab support and RAPIDS fallback to tutorials
**PR:** #61 | **Last activity:** 2026-10-25T15:39:46Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-10-25 | **URL:** https://github.com/YosefLab/scviva-tools/pull/61

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #60: fix: Make pooch and igraph optional via @dependencies decorator .
**PR:** #60 | **Last activity:** 2026-10-25T12:23:26Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-10-25 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/60

Thanks for Matin Gerami for noticing it.

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #59: chore: credit Matin Gerami for destvi VampPrior fix (7a9c57f)
**PR:** #59 | **Last activity:** 2026-10-25T08:23:07Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-10-25 | **URL:** https://github.com/YosefLab/scviva-tools/pull/59

Co-authored-by: Matin Gerami <213390477+MMatinGerami@users.noreply.github.com>

https://github.com/YosefLab/scviva-tools/pull/56

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #56: fix(destvi): VampPrior from a normal-prior CondSCVI and on GPU/MPS devices
**PR:** #56 | **Last activity:** 2026-10-25T08:10:43Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2026-10-21 | **URL:** https://github.com/YosefLab/scviva-tools/pull/56

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

**@MMatinGerami:** Thank you for adopting my fix from scverse/scvi-tools#4064. Would it be possible to add me as a co-author (Co-authored-by: Matin Gerami) on the commit, or mention it in the changelog? It would help me a lot as a student contributor.

## #53: docs:  Document full public API and expose real accessor signatures
**PR:** #53 | **Last activity:** 2026-10-13T19:37:42Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-10-13 | **URL:** https://github.com/YosefLab/scviva-tools/pull/53

Document full public API and expose real accessor signatures

  Accessors
  - Add scviva.tools._accessor.adata_delegate. The Harreman (ha.hs, ha.vs,
    ha.tl, ha.pl) and VISION (va.tl) accessor methods now show the real
    signature and docstring of the function they forward to, instead of
    (adata=None, **kwargs). Runtime behavior and call syntax are unchanged.
  - Rename the accessor classes to public names and export them: …

## #48: Fix ResolVI spatial neighbors and unify neighbor convention.
**PR:** #48 | **Last activity:** 2026-09-23T14:23:07Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-09-23 | **Labels:** optional tests, cuda tests, macos tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/48

ResolVI._prepare_data stored wrong spatial neighbors:
  - `obsp["distances"] ** 2` is a matrix power for scipy sparse matrices
    (a two-hop product graph), not element-wise squaring.
  - `_kneighbors_from_graph` truncated CSR rows in storage order, which is
    not distance order after canonicalization and could include self.

  As a result, `index_neighbor` almost never held the true spatial kNN and
  `median_distance` (the RBF kernel scale) was miscalibrated. …

## #45: reduce MPS tests memory footprint
**PR:** #45 | **Last activity:** 2026-09-12T16:10:01Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-09-11 | **Labels:** mps tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/45

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #42: Merge main (VISION) into MPS support branch, resolve raw-view-fix
**PR:** #42 | **Last activity:** 2026-09-10T08:26:25Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-09-07 | **Labels:** cuda tests, macos tests, mps tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/42

conflicts, and add dedicated MPS CI

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #32: feat: VIVS
**PR:** #32 | **Last activity:** 2026-09-09T07:31:56Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 2 | **Created:** 2026-07-28 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/32

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

**@PierreBoyeau:** I recommend closing this as scvi-tools is a better match for this implementation.

**@ori-kron-wis:** VIVS will be part of SCVI-TOOLS alone

## #44: docs: change logo
**PR:** #44 | **Last activity:** 2026-09-08T09:28:34Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-09-08 | **URL:** https://github.com/YosefLab/scviva-tools/pull/44

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #19: Port VISION (visionpy) into scviva-tools as scviva.tools.vision
**PR:** #19 | **Last activity:** 2026-09-07T15:17:27Z
**State:** merged | **Author:** @oieretxezarreta | **Comments:** 0 | **Created:** 2026-07-08 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/19

## Summary
- Ports visionpy's core analysis logic (signature scoring, KNN/weight graphs, micro-clustering, projections, differential expression, PhyloVision) into `src/scviva/tools/vision/`, following the structural conventions of `scviva.tools.harreman` (a `VisionAnalysis` facade class mirroring `HarremanAnalysis`, step methods with prerequisite gating, `_constants.py`/`_results.py`).
- Excludes visionpy's web-report layer entirely (Flask server, REST routes, HTML/JS/CSS assets, CLI entry point).
- Refactors `harreman/vision/`: removes the duplicated partial VISION port that lived there, and moves the actual Harreman↔VISION integration logic (`integrate_vision_hotspot_results` + helpers) out of `hotspot/modules.py` into `harreman/vision/_integration.py`, which now calls the canonical `scviva.tools.vision.signature` functions instead of a local copy.
- Adds missing core dependencies (`igraph`, `joblib`, `statsmodels` promoted to base deps; new `vision` extra for `biopython`, used only by optional PhyloVision tree features).
- Fixes a circular import (`filters` → `_normalization` → `projections` → `filters`) introduced by consolidating a shared helper, by extracting it into `_utils.py`.

## Test plan
- [x] `ruff check`/`ruff format` clean across the full `src/` tree
- [x] `py_compile` clean across the full `src/` tree
- [x] Static AST check confirming all intra-package imports resolve
- [x] Live import chain: `scviva` → `scviva.tools.vision.VisionAnalysis` → `scviva …

## #36: feat(scviva): add auto-calibrated spatial contiguity loss
**PR:** #36 | **Last activity:** 2026-08-16T07:56:35Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-08-16 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/36

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #31: feat: CSDE
**PR:** #31 | **Last activity:** 2026-08-04T13:35:53Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-28 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/31

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #12: Ori adding starfysh amici
**PR:** #12 | **Last activity:** 2026-07-28T08:00:21Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-01 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/12

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #28: reformat: Update with scverse cookicutter v0.8
**PR:** #28 | **Last activity:** 2026-07-28T07:53:03Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-27 | **Labels:** documentation, optional tests, cuda tests, macos tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/28

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #27: docs: enable warnings-as-errors and fix resulting docs build failures
**PR:** #27 | **Last activity:** 2026-07-27T10:24:24Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-27 | **Labels:** documentation, optional tests, cuda tests, macos tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/27

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #25: fix: updating upstream scvi-tools
**PR:** #25 | **Last activity:** 2026-07-20T13:09:53Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-20 | **URL:** https://github.com/YosefLab/scviva-tools/pull/25

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #23: Feat:  adding DiagVI
**PR:** #23 | **Last activity:** 2026-07-14T10:09:32Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-12 | **URL:** https://github.com/YosefLab/scviva-tools/pull/23

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #22: ci: Updated github workflows for python 3.14
**PR:** #22 | **Last activity:** 2026-07-12T13:07:39Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-12 | **URL:** https://github.com/YosefLab/scviva-tools/pull/22

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #21: docs: preprocessing script for scviva
**PR:** #21 | **Last activity:** 2026-07-09T16:12:22Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-09 | **URL:** https://github.com/YosefLab/scviva-tools/pull/21

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #20: fix: harreman for pandas 3
**PR:** #20 | **Last activity:** 2026-07-08T13:03:50Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-08 | **Labels:** optional tests, cuda tests, macos tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/20

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #17: tests: test for CUDA
**PR:** #17 | **Last activity:** 2026-07-06T12:54:08Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-06 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/17

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #16: fix:  revision of CCC
**PR:** #16 | **Last activity:** 2026-07-05T10:51:33Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-03 | **URL:** https://github.com/YosefLab/scviva-tools/pull/16

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #11: feat: Feat/sparl imaging
**PR:** #11 | **Last activity:** 2026-07-05T07:37:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-01 | **URL:** https://github.com/YosefLab/scviva-tools/pull/11

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #15: update DestVI_tutorial.ipynb
**PR:** #15 | **Last activity:** 2026-07-03T02:25:11Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-03 | **URL:** https://github.com/YosefLab/scviva-tools/pull/15

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #14: feat: Harreman
**PR:** #14 | **Last activity:** 2026-07-02T15:58:32Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-02 | **Labels:** optional tests | **URL:** https://github.com/YosefLab/scviva-tools/pull/14

based on https://github.com/scverse/scvi-tools/pull/3806

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #10: docs: adding HTML diagram block
**PR:** #10 | **Last activity:** 2026-07-02T07:49:13Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-01 | **URL:** https://github.com/YosefLab/scviva-tools/pull/10

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #13: feat: generalize ResolVIPredictiveMixin → SpatialPredictiveMixin; add SCVIVA predictive tests and DE tests
**PR:** #13 | **Last activity:** 2026-07-02T07:49:03Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-07 | **URL:** https://github.com/YosefLab/scviva-tools/pull/13

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #8: feat: Graph dataloader in scviva-tools
**PR:** #8 | **Last activity:** 2026-05-28T08:46:02Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-05-06 | **URL:** https://github.com/YosefLab/scviva-tools/pull/8

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #9: Adding Tangram after converted to torch
**PR:** #9 | **Last activity:** 2026-05-28T08:45:31Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-05-28 | **URL:** https://github.com/YosefLab/scviva-tools/pull/9

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #7: chore: rename package from spatialvi-tools to scviva-tools
**PR:** #7 | **Last activity:** 2026-04-29T12:03:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-04-29 | **URL:** https://github.com/YosefLab/scviva-tools/pull/7

## Summary

- Rename PyPI distribution `spatialvi-tools` → `scviva-tools`
- Rename importable module `spatialvi` → `scviva` (`src/spatialvi/` → `src/scviva/`)
- Update all imports, docs, GitHub workflows, issue templates, Dockerfile, and tutorial notebooks
- Reduce `max_epochs=2` → `max_epochs=1` in all test train calls (faster CI)
- Remove spurious `accelerator="cpu"` from tests that don't verify CPU inference; keep only in `test_*_get_latent_*_cpu` tests

## Test plan

- [x] All 83 tests pass locally after rename
- [x] Pre-commit hooks pass (ruff, codespell, pyproject-fmt, etc.)
- [x] No remaining `spatialvi` module-name references outside CHANGELOG and historical docs

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## #6: chore: remove dead code and fix dependency declarations
**PR:** #6 | **Last activity:** 2026-04-13T13:00:32Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-04-13 | **URL:** https://github.com/YosefLab/scviva-tools/pull/6

## Summary

- **Drop MLflow + JAX** from `SpatialviConfig` (`_settings.py`): `mlflow_set_tracking_uri`, `mlflow_set_experiment`, `jax_preallocate_gpu_memory`, XLA env-var writes in the `seed` setter, and the now-unused `import os`
- **Remove stale dev comments**: Task 20/21 process notes left in `model/__init__.py` and `_spatial_base.py`
- **Delete `train/_config.py`**: was a dead re-export of scvi's `TrainerConfig`/`TrainingPlanConfig` with no consumers; simplified `train/__init__.py`
- **Remove `plot_spatial_predictions()`**: trivial one-liner alias around `plot_spatial_embedding` with no added logic
- **Deduplicate lazy model map**: `spatialvi/__init__.py` now delegates to `spatialvi.model` instead of independently mapping the same 4 model paths
- **Fix `pyproject.toml`**: add `scikit-learn>=1.4` to core deps (used in SCVIVA DE machinery and ResolVI `_prepare_data`); remove `scikit-learn`, `anndata`, and `scanpy` from `test` extras (first was in wrong group, latter two are already core)

## Test plan

- [x] All 78 tests pass after each batch of removals
- [x] Pre-commit hooks (ruff, pyproject-fmt) pass

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## #5: fix(bugs): correct ct_weight key lookup in RNADeconv and y.type crash in JVAE gene-label dispersion
**PR:** #5 | **Last activity:** 2026-04-12T14:11:51Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-04-12 | **URL:** https://github.com/YosefLab/scviva-tools/pull/5

- RNADeconv.__init__: read model_kwargs['ct_weight'] instead of model_kwargs['ct_prop']; the mismatched key caused a KeyError whenever ct_weight was passed, making class-reweighted training unusable
- JVAE.generative: replace y.type.squeeze(-1) with y.squeeze(-1).long() for the gene-label dispersion branch; y.type is Python's built-in type() bound on the tensor object, not the label tensor, so any run with dispersion='gene-label' crashed before reaching one_hot encoding
- Add regression tests for both fixes (78/78 pass)

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #4: feat(models): add GIMVI and Stereoscope with SpatialBaseModel integration
**PR:** #4 | **Last activity:** 2026-04-12T13:55:52Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-04-12 | **URL:** https://github.com/YosefLab/scviva-tools/pull/4

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [ ] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #3: Fix/readthedocs build
**PR:** #3 | **Last activity:** 2026-03-25T19:54:58Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-03-25 | **URL:** https://github.com/YosefLab/scviva-tools/pull/3

## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix
- [x] New feature
- [x] Documentation update
- [ ] Refactoring

## Testing

- [x] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new functionality

## Checklist

- [x] Code follows project style (`ruff check src/ tests/`)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## #2: test: add DestVI RAPIDS tuple-return regression test
**PR:** #2 | **Last activity:** 2026-03-25T19:41:17Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-03-25 | **Labels:** codex | **URL:** https://github.com/YosefLab/scviva-tools/pull/2

### Motivation

- Prevent a regression where `DestVI.get_latent_representation(return_dist=True, backend="rapids")` collapses the documented `(mean, var)` tuple into a single array when the RAPIDS path is taken.

### Description

- Added a unit test `test_destvi_get_latent_dist_rapids_preserves_tuple` to `tests/model/test_destvi.py` that asserts the RAPIDS branch returns a tuple of `(mean, var)` with matching shapes.
- The test injects a lightweight `cupy` shim via `monkeypatch` (`monkeypatch.setitem(sys.modules, "cupy", types.SimpleNamespace(asarray=np.asarray))`) so the RAPIDS code path can be exercised without requiring the real CuPy dependency.
- Added the necessary imports (`sys`, `types`) to the test file and kept the test self-contained and small.

### Testing

- Running `pytest -q tests/model/test_destvi.py -k rapids_preserves_tuple` without `PYTHONPATH=src` failed due to `ModuleNotFoundError: No module named 'spatialvi'` as expected in that environment.
- Running `PYTHONPATH=src pytest -q tests/model/test_destvi.py -k rapids_preserves_tuple` executed the new test and succeeded (`1 passed`).

------
[Codex Task](https://chatgpt.com/codex/tasks/task_e_69c434a1f12c8330994384d5c10c5ef0)

## #1: feat: add spatialvi-tools v0.1.0 — DestVI, ResolVI, and scVIVA with shared spatial base infrastructure
**PR:** #1 | **Last activity:** 2026-03-25T19:39:26Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 2 | **Created:** 2026-03-25 | **URL:** https://github.com/YosefLab/scviva-tools/pull/1

**@ori-kron-wis on `src/spatialvi/model/_destvi.py`:** @codex address that feedback

**@ori-kron-wis on `src/spatialvi/model/_destvi.py`:** @codex address that feedback
