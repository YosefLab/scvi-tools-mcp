# scverse/scvi-colab GitHub Pull Requests

4 pull requests (open, closed and merged, bots excluded) from scverse/scvi-colab with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; PRs are only removed once they age out of that window.

## #57: build: switch poetry to hatchling build
**PR:** #57 | **Last activity:** 2026-07-28T06:20:50Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2026-07-28 | **URL:** https://github.com/scverse/scvi-colab/pull/57

**@ori-kron-wis:** close https://github.com/scverse/scvi-colab/issues/5

## #33: fix: remove deps of ContextualVersionConflict
**PR:** #33 | **Last activity:** 2026-02-09T11:57:38Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-02-09 | **URL:** https://github.com/scverse/scvi-colab/pull/33

## #4: add uv as installer
**PR:** #4 | **Last activity:** 2025-01-27T13:35:43Z
**State:** closed | **Author:** @jhuang-ptgg | **Comments:** 2 | **Created:** 2025-01-23 | **URL:** https://github.com/scverse/scvi-colab/pull/4

The purpose of this PR is to add uv support to the install() function. in my test on colab, uv pip install --system is much faster than pip install. Although uv is installed in all colab instances I ran recently, a try clause is added to test whether uv is installed in the instance.

**@jhuang-ptgg:** This may need to be modified after PR #3 is approved and merged to main branch

**@ori-kron-wis:** thank you @jhuang-ptgg , yes this is exactly what we want to fix.
we will re release scvi-colab after that.

## #3: ci: updating scvi-colab
**PR:** #3 | **Last activity:** 2025-01-26T13:12:12Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-01-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-colab/pull/3

scvi-colab updates
Seems install take a lot of time

**@ori-kron-wis:** close https://github.com/scverse/scvi-colab/pull/4
