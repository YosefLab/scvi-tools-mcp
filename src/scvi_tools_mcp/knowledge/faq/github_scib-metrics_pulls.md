# YosefLab/scib-metrics GitHub Pull Requests

61 pull requests (open, closed and merged, bots excluded) from YosefLab/scib-metrics with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; PRs are only removed once they age out of that window.

## #306: release: v0.6.2
**PR:** #306 | **Last activity:** 2026-11-01T10:19:26Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-11-01 | **URL:** https://github.com/YosefLab/scib-metrics/pull/306

## #305: fix: get_results(min_max_scale=True) on pandas 3
**PR:** #305 | **Last activity:** 2026-11-01T10:07:00Z
**State:** merged | **Author:** @Marius1311 | **Comments:** 1 | **Created:** 2026-10-30 | **URL:** https://github.com/YosefLab/scib-metrics/pull/305

On pandas 3, `Benchmarker.get_results(min_max_scale=True)` raises `TypeError: Invalid value 'Aggregate score' for dtype 'float64'`. Min-max scaling makes the aggregate score columns float64, and pandas 3 no longer upcasts a column when a string is written into it (it warned before).

The aggregate columns are now cast to `object` before `'Aggregate score'` is written, as the metric columns already are. The new test fails on pandas 3.1 without the fix and passes with it; the existing tests never pass `min_max_scale=True`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

**@ori-kron-wis:** @Marius1311 Approved. Can you also please add a changelog for version 0.6.2?

## #276: ci: update github workflows
**PR:** #276 | **Last activity:** 2026-10-11T07:30:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-12 | **URL:** https://github.com/YosefLab/scib-metrics/pull/276

## #287: fix: raise clear errors for degenerate single-batch inputs, fix aggregate score font color
**PR:** #287 | **Last activity:** 2026-08-13T11:30:10Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-08-13 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scib-metrics/pull/287

close https://github.com/YosefLab/scib-metrics/issues/100
close https://github.com/YosefLab/scib-metrics/issues/62
close https://github.com/YosefLab/scib-metrics/issues/58

## #284: feat: pertubation predictive score
**PR:** #284 | **Last activity:** 2026-08-12T08:13:18Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-08-10 | **Labels:** cuda tests | **URL:** https://github.com/YosefLab/scib-metrics/pull/284

## #267: Add sBEE metric and bump version to 0.6.0
**PR:** #267 | **Last activity:** 2026-07-28T11:51:58Z
**State:** merged | **Author:** @MekanMyradov | **Comments:** 2 | **Created:** 2026-05-16 | **URL:** https://github.com/YosefLab/scib-metrics/pull/267

## Summary

- Add sBEE (single-cell Batch Effect Evaluator) as a new batch correction metric
- Wire sbee into the benchmark pipeline (`BatchCorrection`, `MetricAnnDataAPI`, `metric_name_cleaner`) using 90-neighbor resolution
- Add tests (`test_sbee.py`, update `test_benchmarker.py`)
- Add API docs entry, changelog entry, and DOI citation in `references.bib`

## Test plan

- [x] All tests pass (`pytest`)
- [x] Docs build successfully (`cd docs && make html`)
- [x] Pre-commit hooks pass

**@MekanMyradov:** Dear @ori-kron-wis,

Can you please approve/reject the PR.

Thanks
Mekan

**@ori-kron-wis:** We will review it in the coming days , thank you @MekanMyradov

## #278: Update template to v0.8.0
**PR:** #278 | **Last activity:** 2026-07-28T08:34:31Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 1 | **Created:** 2026-07-17 | **URL:** https://github.com/YosefLab/scib-metrics/pull/278

`cookiecutter-scverse` released [v0.8.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.8.0).

## Changes

This release comes with a bunch of smaller fixes and changes to the template, and a lot of under-the-hood changes reducing friction with template sync and initialization.

## Changes

The most notable change is the introduction of [zizmor](https://github.com/zizmorcore/zizmor) as pre-commit hook for hardening github actions against supply-chain attacks. Github actions will be pinned to an immutable hash instead of a version number. Dependabot will take care of updating them (by `@ilan-gold`, `@grst`, `@ilia-kats` in https://github.com/scverse/cookiecutter-scverse/pull/498).

Additionally, we introduced a helper package, [scverse-misc](https://github.com/scverse/scverse-misc), that contains utility code shared across scverse core and ecosystem packages. As an initial step, we moved custom sphinx extensions that were previously part of the template into scverse-misc (by `@ilia-kats` in https://github.com/scverse/cookiecutter-scverse/pull/529). Rollout of additional features (shared logging and settings) will follow in the next release.

The remaining changes are listed below:

## Updates to the template

 * ci: remove hacks for docs building by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/462
 * ci: list all installed packages in CI output by `@grst` in https://github.com/scverse/cookiecutter-scverse/pull/469
 * …

**@ori-kron-wis:** merged in other PR

## #83: [WIP] cell mixing score
**PR:** #83 | **Last activity:** 2026-07-28T08:32:41Z
**State:** open | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2023-02-16 | **URL:** https://github.com/YosefLab/scib-metrics/pull/83

## #259: feat: Spatial Conservation Metrics for scib-metrics
**PR:** #259 | **Last activity:** 2026-07-28T08:27:27Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-03-10 | **URL:** https://github.com/YosefLab/scib-metrics/pull/259

## #273: fix: replace jax vmap
**PR:** #273 | **Last activity:** 2026-07-28T08:22:20Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-18 | **URL:** https://github.com/YosefLab/scib-metrics/pull/273

## #280: build: update to scverse cookiecutter template v0.8.0
**PR:** #280 | **Last activity:** 2026-07-28T08:04:32Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-27 | **Labels:** documentation, cuda tests | **URL:** https://github.com/YosefLab/scib-metrics/pull/280

Move packaging to PEP 735 dependency-groups with hatch test/docs envs,
  rewrite CI around a hatch-driven test matrix, switch pre-commit to
  biome/pyproject-fmt/zizmor. Drop Python 3.11, add 3.14 support.
  Bump version to 0.6.0.

## #248: Update template to v0.7.0
**PR:** #248 | **Last activity:** 2026-07-17T07:12:02Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-12-24 | **URL:** https://github.com/YosefLab/scib-metrics/pull/248

`cookiecutter-scverse` released [v0.7.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.7.0).

## Changes

## Changes

* Switch to dependency groups in pyproject.toml by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/449
* Use type instead of label for issue templates by `@Zethson` in https://github.com/scverse/cookiecutter-scverse/pull/444
* use KaTeX Sphinx plugin for better math rendering `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/446
* Make all-green check pass even if pre-release job fails by @grst in https://github.com/scverse/cookiecutter-scverse/pull/452

## Fixes

* sphinx conf.py: use project instead of project_name by `@ilia-kats` in https://github.com/scverse/cookiecutter-scverse/pull/440
* Fix workflow badge and link in readme by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/441
* Enable OIDC in Codecov action by `@grst` in https://github.com/scverse/cookiecutter-scverse/pull/457


## Additional remarks
* **unsubscribe**: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete the `.cruft.json` file in the root of your repository.
* If there are **merge conflicts**, you need to resolve them manually.
* The scverse template works best when the [pre-commit.ci][], [readthedocs][] and [codecov][] services are enabled.
  Make sure to activate …

## #256: Update changelog for kbet calculation fix
**PR:** #256 | **Last activity:** 2026-05-27T08:31:10Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-02-26 | **URL:** https://github.com/YosefLab/scib-metrics/pull/256

## #254: fix: update kbet calc with new numpy
**PR:** #254 | **Last activity:** 2026-05-23T15:30:29Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-02-22 | **URL:** https://github.com/YosefLab/scib-metrics/pull/254

## #240: Fix: set seed for Leiden clustering
**PR:** #240 | **Last activity:** 2026-01-28T07:00:24Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-10-28 | **URL:** https://github.com/YosefLab/scib-metrics/pull/240

## #234: feat: Adding mudata support for benchmarker
**PR:** #234 | **Last activity:** 2025-12-29T06:30:46Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-09-28 | **URL:** https://github.com/YosefLab/scib-metrics/pull/234

**@ori-kron-wis:** Found out that the PR is redundant

## #229: feat: added solver selection to benchmarker for arpack stability issues + moving to py313
**PR:** #229 | **Last activity:** 2025-12-13T13:15:57Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-09-14 | **URL:** https://github.com/YosefLab/scib-metrics/pull/229

**@ori-kron-wis:** also removed py3.10 and added py3.13 in this PR

## #217: feat: adding BRAS to benchmarker
**PR:** #217 | **Last activity:** 2025-10-27T08:29:52Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-07-08 | **URL:** https://github.com/YosefLab/scib-metrics/pull/217

see: https://github.com/YosefLab/scib-metrics/pull/197 and: https://github.com/YosefLab/scib-metrics/issues/218

**@ori-kron-wis:** instead of regular silhouette batch

## #236: Update template to v0.6.0
**PR:** #236 | **Last activity:** 2025-10-15T07:40:53Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-09-30 | **URL:** https://github.com/YosefLab/scib-metrics/pull/236

`cookiecutter-scverse` released [v0.6.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.6.0).

## Changes

## CI updates

We now more consistently embrace hatch and uv in the template. CI now generates the job matrix from that hatch configuration. This means the `pyproject.toml` file is now the one **single** point of truth for both local and CI test jobs.

* Get test matrix from hatch by @grst in https://github.com/scverse/cookiecutter-scverse/pull/390
* Enable parallel testing with hatch by @grst in https://github.com/scverse/cookiecutter-scverse/pull/430
* chore: update code cov by `@ilan-gold` in https://github.com/scverse/cookiecutter-scverse/pull/427
* Fix remaining uv cache globs in workflows by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/388
* Switch root tests to uv by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/384
* Fix uv cache glob for script tests by `@flying-sheep` in https://github.com/scverse/cookiecutter-scverse/pull/387
* Test pre-release dependencies by @grst in https://github.com/scverse/cookiecutter-scverse/pull/393
* Use hatch on RTD by @grst in https://github.com/scverse/cookiecutter-scverse/pull/402
* Fix ruff-check naming by `@Zethson` in https://github.com/scverse/cookiecutter-scverse/pull/414
* fix codecov upload (closes #381) by `@ilia-kats` in https://github.com/scverse/cookiecutter-scverse/pull/382


## Documentation updates

We improved the "contributing …

## #215: fix: min_max_scale=False should be default in .get_results
**PR:** #215 | **Last activity:** 2025-10-05T13:00:09Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-07-07 | **URL:** https://github.com/YosefLab/scib-metrics/pull/215

close https://github.com/YosefLab/scib-metrics/issues/205

## #213: Revert "Skip labels before loop"
**PR:** #213 | **Last activity:** 2025-10-05T12:30:35Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2025-06-29 | **URL:** https://github.com/YosefLab/scib-metrics/pull/213

Reverts YosefLab/scib-metrics#180

Bug in the implementation skip the wrong clusters

Fixes #212

## #198: Update template to v0.5.0
**PR:** #198 | **Last activity:** 2025-09-14T07:17:54Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-04-02 | **URL:** https://github.com/YosefLab/scib-metrics/pull/198

`cookiecutter-scverse` released [v0.5.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.5.0).

## Changes

### New template sync

We re-implemented template sync from scratch instead on relying on cruft. This allows us to create *real merge conflicts* that show up as such on GitHub instead of `.rej` files.

* Generate real merge conflicts on template update by @grst in https://github.com/scverse/cookiecutter-scverse/pull/364

### Enhancements

We committed to using [hatch](https://hatch.pypa.io/latest/) as project and environment manager. By doing so, we simplified the
GitHub actions:
* Hatch envs by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/308
* Upgrade Github actions by @Zethson in https://github.com/scverse/cookiecutter-scverse/pull/324
* Use hatch in github actions by @grst in https://github.com/scverse/cookiecutter-scverse/pull/373

We switched the pre-commit hook from prettier to biome and added a pre-commit hook for autoformatting `pyproject.toml` files:
* Switch from prettier to Biome by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/304
* TOML formatting using pyproject-fmt by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/299

We added (optional) integration with VScode and improved cookiecutter prompts:
* Add VS Code integration by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/312
* Add prompts for most variables by @flying-she …

## #197: Add fast BRAS implementation to scib-metrics package.
**PR:** #197 | **Last activity:** 2025-09-01T11:30:24Z
**State:** merged | **Author:** @prauten | **Comments:** 13 | **Created:** 2025-04-02 | **URL:** https://github.com/YosefLab/scib-metrics/pull/197

Hi there,

I am Pia, the first author of the preprint "[Metrics Matter: Why We Need to Stop Using Silhouette in Single-Cell Benchmarking](https://www.biorxiv.org/content/10.1101/2025.01.21.634098v1.full-text)" mentioned in issue #193.

First, thank you for developing and maintaining this package. It is a valuable resource for the community and much needed considering ever-increasing data set sizes.

Our preprint highlights limitations of silhouette-based metrics for evaluating batch effect removal, particularly in the presence of prevalent nested batch effects. To address these challenges, we propose a new metric called BRAS (batch removal adapted silhouette), which redefines the silhouette score to be robust against such effects. Integrating BRAS into your package would allow users to explore what our work suggests is a more reliable alternative to current silhouette-based metrics for benchmarking integration methods.

I have prepared a pull request implementing BRAS with minimal, backward-compatible changes. This implementation builds on the existing package structure and functionality and includes appropriate documentation. I would greatly appreciate the opportunity to collaborate on integrating this contribution!

Let me know if you would like any adjustments or further context.

Best,
Pia

**@adamgayoso on `src/scib_metrics/utils/_silhouette.py`:** Would be great to check all options explicitly and have the else raise an error

**@adamgayoso on `CHANGELOG.md`:** ```suggestion
- Add batch removal adapted silhouette (BRAS) metric ({func}`scib_metrics.metrics.bras`) {pr}`197`, which addresses limitations of silhouette for scoring batch effect removal.
```

**@adamgayoso on `CHANGELOG.md`:** ```suggestion
- Changed {func}`scib_metrics.utils.cdist` to support cosine distance.
```

**@adamgayoso on `src/scib_metrics/metrics/_silhouette.py`:** ```suggestion
    Additional options enable BRAS compatible usage (see :func:`~scib_metrics.metrics.bras` documentation).
```

**@adamgayoso on `src/scib_metrics/utils/_silhouette.py`:** ```suggestion
     of evaluating data integration (see :func:`~scib_metrics.metrics.bras` documentation).
```

**@adamgayoso (review, changes requested):** Thanks! Some small changes suggested. In a follow-up PR, would you like to add this to the benchmarker? Specifically just the dataclass and the enum should be necessary.

**@prauten:** Hi Adam,

Thanks for your swift response and code reviews!

It is a great idea to add the BRAS metric to the benchmarker. Once I get to it, I'll open a separate pull request.

Best,
Pia

**@prauten on `src/scib_metrics/utils/_silhouette.py`:** Thanks for the suggestion, I will implement it and update the pull request.

**@prauten on `src/scib_metrics/utils/_silhouette.py`:** Marking this as resolved.

**@adamgayoso on `CHANGELOG.md`:** Can you move these into the unreleased section above?

**@adamgayoso (review, approved):** LGTM. Please move the release notes up for now. Thanks.

**@prauten on `CHANGELOG.md`:** I did! Apologies for the oversight. I thought version 0.5.4 had not been released yet, as it doesn't show as "latest" on the main page of the package on GitHub.

**@prauten:** Thank you for including BRAS in your package and reviewing my PR!

## #203: fix: update default init values for benchmarker
**PR:** #203 | **Last activity:** 2025-07-22T06:30:14Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-04-22 | **URL:** https://github.com/YosefLab/scib-metrics/pull/203

update to bio_conservation_metrics, batch_correction_metrics deafult values

## #180: Skip labels before loop
**PR:** #180 | **Last activity:** 2025-07-05T20:30:10Z
**State:** merged | **Author:** @johnarevalo | **Comments:** 0 | **Created:** 2024-09-24 | **URL:** https://github.com/YosefLab/scib-metrics/pull/180

Following https://github.com/theislab/scib/pull/394

## #179: Make get_results work, if either no BatchCorrection or BioConservation metrics.
**PR:** #179 | **Last activity:** 2025-07-05T20:30:08Z
**State:** closed | **Author:** @LArnoldt | **Comments:** 1 | **Created:** 2024-09-06 | **URL:** https://github.com/YosefLab/scib-metrics/pull/179

Make get_results work, if either no BatchCorrection or BioConservation metrics. See #https://github.com/YosefLab/scib-metrics/issues/157.

**@adamgayoso:** This was addressed in #181, thank you for raising!

## #196: Update CHANGELOG.md
**PR:** #196 | **Last activity:** 2025-06-28T07:30:04Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-03-30 | **URL:** https://github.com/YosefLab/scib-metrics/pull/196

## #189: fix: revert the update  for _core.py
**PR:** #189 | **Last activity:** 2025-05-18T10:00:23Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-17 | **URL:** https://github.com/YosefLab/scib-metrics/pull/189

## #188: feat: support scvi-tools scib-metric autotune
**PR:** #188 | **Last activity:** 2025-05-13T22:30:11Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-12 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/pull/188

added option for missing group of metrics and fill in with 0.5

## #182: Fix Lisi return type and docstring
**PR:** #182 | **Last activity:** 2025-02-02T09:00:28Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-11-04 | **URL:** https://github.com/YosefLab/scib-metrics/pull/182

Closes #113

## #181: Change behavior of None default metrics and allow results/plotting to work with bio/batch separately.
**PR:** #181 | **Last activity:** 2025-02-02T08:30:04Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-11-03 | **URL:** https://github.com/YosefLab/scib-metrics/pull/181

Closes #157

## #177: Add more ruff rules
**PR:** #177 | **Last activity:** 2024-11-30T16:30:18Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-29 | **URL:** https://github.com/YosefLab/scib-metrics/pull/177

## #174: Typing fixes
**PR:** #174 | **Last activity:** 2024-11-20T08:30:25Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-22 | **URL:** https://github.com/YosefLab/scib-metrics/pull/174

## #165: Update template to v0.4.0
**PR:** #165 | **Last activity:** 2024-11-20T08:30:16Z
**State:** merged | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2024-05-21 | **URL:** https://github.com/YosefLab/scib-metrics/pull/165

`cookiecutter-scverse` released [v0.4.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.4.0).

## Changes

## What's Changed
* pre-commit updates
* Fix installation instructions on contributing guide by @grst in https://github.com/scverse/cookiecutter-scverse/pull/271
* fix typo by @Zethson in https://github.com/scverse/cookiecutter-scverse/pull/279
* Use cookiecutter variable for project repo in conf.py by @Zethson in https://github.com/scverse/cookiecutter-scverse/pull/278
* Add node_modules to .gitignore by @Zethson in https://github.com/scverse/cookiecutter-scverse/pull/277
* Update required python versions according to scientific python SPEC 0 by @grst in https://github.com/scverse/cookiecutter-scverse/pull/284
* Require myst-nb >= 1.1.0 by @grst in https://github.com/scverse/cookiecutter-scverse/pull/285


**Full Changelog**: https://github.com/scverse/cookiecutter-scverse/compare/v0.3.1...v0.4.0

## Additional remarks
* unsubscribe: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete your `.cruft` file.
* If there are **merge conflicts**,
  they either show up inline (`>>>>>>>`) or a `.rej` file will have been created for the respective files.
  You need to address these conflicts manually. Make sure to enable pre-commit.ci (see below) to detect such files.
* The scverse template works best when the [pre-commit.ci][], [r …

## #173: Add seed to leiden clustering
**PR:** #173 | **Last activity:** 2024-11-20T07:30:31Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-21 | **URL:** https://github.com/YosefLab/scib-metrics/pull/173

Fixes #104

## #171: Fix warnings
**PR:** #171 | **Last activity:** 2024-11-19T21:30:22Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-21 | **URL:** https://github.com/YosefLab/scib-metrics/pull/171

## #172: Fix kmeans test instability
**PR:** #172 | **Last activity:** 2024-11-19T21:01:21Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-21 | **URL:** https://github.com/YosefLab/scib-metrics/pull/172

## #170: Use new scanpy umap connectivity fn in test
**PR:** #170 | **Last activity:** 2024-11-19T20:30:34Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-08-21 | **URL:** https://github.com/YosefLab/scib-metrics/pull/170

## #107: Drop Python 3.8 and fix one-hot error
**PR:** #107 | **Last activity:** 2024-08-24T15:00:52Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2023-09-18 | **URL:** https://github.com/YosefLab/scib-metrics/pull/107

Fixes #105

## #108: Fix isolated label score
**PR:** #108 | **Last activity:** 2024-08-22T15:20:14Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2023-09-18 | **URL:** https://github.com/YosefLab/scib-metrics/pull/108

This fixes an error in how the isolated label score is computed. This puts the package in line with this change https://github.com/theislab/scib/pull/370/ in the original package

## #152: add progress bar arg to benchmarker
**PR:** #152 | **Last activity:** 2024-03-01T21:19:18Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-29 | **URL:** https://github.com/YosefLab/scib-metrics/pull/152

Added `progress_bar` argument that lets users disable the progress bar in `Benchmarker`. I also noticed that the progress bar style does not adjust based on the settings - filed an issue here: #153. It might also make sense to allow `None` for `settings.progress_bar_style` and then disable it directly if so.

## #151: [releases] add date to 0.5.1, start 0.6.0
**PR:** #151 | **Last activity:** 2024-02-29T21:27:17Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-29 | **URL:** https://github.com/YosefLab/scib-metrics/pull/151

## #149: [misc] move metric files to directory
**PR:** #149 | **Last activity:** 2024-02-23T23:45:06Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/149

## #148: [docs] update docstrings
**PR:** #148 | **Last activity:** 2024-02-23T23:27:23Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/148

## #52: initial benchmarker and plotting
**PR:** #52 | **Last activity:** 2024-02-23T23:05:58Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 16 | **Created:** 2022-11-13 | **URL:** https://github.com/YosefLab/scib-metrics/pull/52

Fixes #13
Fixes #14
Fixes #41

See the rendered docs for the new tutorial and new classes.

**@adamgayoso on `pyproject.toml`:** ```suggestion
    "ipython!=8.7.0", # code highlighting issue
```

**@martinkim0 on `src/scib_metrics/utils/_pcr.py`:** ```suggestion
        covariate = one_hot(np.asarray(pd.Categorical(covariate).codes))
```

**@martinkim0 on `src/scib_metrics/utils/_pcr.py`:** ```suggestion
        covariate = np.asarray(covariate)
        covariate = covariate.reshape((covariate.shape[0], 1))
```

**@martinkim0 on `src/scib_metrics/utils/_pcr.py`:** ```suggestion
```

**@adamgayoso on `src/scib_metrics/utils/_pcr.py`:** this happens on line 48 though!

**@adamgayoso on `src/scib_metrics/utils/_pcr.py`:** same here! I think we should take care of all input validations in a future PR

**@adamgayoso on `src/scib_metrics/utils/_pcr.py`:** oh didn't see this. I will make the change!

**@justjhong on `src/scib_metrics/benchmark/_core.py`:** instead of a callable why not the user pass in a dict of kwargs and create the partial callable here if they passed in a dict instead of `True`.

**@justjhong on `src/scib_metrics/benchmark/_core.py`:** This would avoid the user having to match the correct scib_metrics fn to the one they want to specify kwargs for and prevent unintentional mismatch between labels and actual metric fns.

**@justjhong on `src/scib_metrics/benchmark/_core.py`:** should this fn avoid incomplete overrides of results? It seems like there are few to no cases where it should be called multiple times but it would just redo computation here. Specifically confusing in cases where somebody calls benchmark againintentionally after tweaking metrics they want to run, this would result in a mishmash of old and new results.

**@justjhong on `src/scib_metrics/benchmark/_core.py`:** is this split based on the paper?

**@justjhong on `src/scib_metrics/benchmark/_core.py`:** :o

**@justjhong (review, approved):** looks awesome!!

**@adamgayoso on `src/scib_metrics/benchmark/_core.py`:** yes

**@adamgayoso on `src/scib_metrics/benchmark/_core.py`:** I'll add a comment

**@adamgayoso on `src/scib_metrics/benchmark/_core.py`:** can use frozen in the metrics dataclasses so that it wouldn't be possible to run benchmark with different metrics

## #42: Reimplement silhouette in a mem constant way, pdist using lax scan
**PR:** #42 | **Last activity:** 2024-02-23T23:05:57Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 6 | **Created:** 2022-10-25 | **URL:** https://github.com/YosefLab/scib-metrics/pull/42

Fixes #36

Our implementation now exactly follows the algorithm used in sklearn (instead of computing full X pairwise distance matrix, compute it in vertical chunks `cdist(X_chunk_size, X)` and then aggregate intra and inter clust dists

**@martinkim0 on `src/scib_metrics/utils/_silhouette.py`:** ```suggestion
    return get_ndarray(jnp.nan_to_num(sil_samples))
```
from `utils`.

**@martinkim0 on `src/scib_metrics/utils/_silhouette.py`:** Is there a reason why `jnp` wasn't used here?

**@martinkim0 on `src/scib_metrics/utils/_silhouette.py`:** ```suggestion
from ._types import NdArray
```

**@martinkim0 on `src/scib_metrics/utils/_silhouette.py`:** ```suggestion
```

**@martinkim0 on `src/scib_metrics/utils/_dist.py`:** nice

**@adamgayoso on `src/scib_metrics/utils/_silhouette.py`:** Nope.

## #139: Update template to v0.3.1
**PR:** #139 | **Last activity:** 2024-02-23T22:35:02Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 1 | **Created:** 2024-02-22 | **URL:** https://github.com/YosefLab/scib-metrics/pull/139

`cookiecutter-scverse` released [v0.3.1](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.3.1).

## Changes

## Enhancements
* Use Ruff formatting, run Ruff on notebooks by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/256

## Fixes
* Unpin node version, pre-commit autoupdate by @pre-commit-ci in https://github.com/scverse/cookiecutter-scverse/pull/255
* Fix copy without render by @grst in https://github.com/scverse/cookiecutter-scverse/pull/263
* Fix Ruff deprecations by @flying-sheep in https://github.com/scverse/cookiecutter-scverse/pull/267

## Documentation
* Update contributing.md by @grst in https://github.com/scverse/cookiecutter-scverse/pull/259


**Full Changelog**: https://github.com/scverse/cookiecutter-scverse/compare/v0.3.0...v0.3.1

## Additional remarks
* unsubscribe: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete your `.cruft` file.
* If there are **merge conflicts**,
  they either show up inline (`>>>>>>>`) or a `.rej` file will have been created for the respective files.
  You need to address these conflicts manually. Make sure to enable pre-commit.ci (see below) to detect such files.
* The scverse template works best when the [pre-commit.ci][], [readthedocs][] and [codecov][] services are enabled.
  Make sure to activate those apps if you haven't already.

[`template-repos.yml`]: …

**@martinkim0:** Will skip this update since we've updated the cruft config with #147

## #147: [misc] skip workflows, pre-commit, pyproject in template sync
**PR:** #147 | **Last activity:** 2024-02-23T22:33:33Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/147

## #146: [misc] remove bumpversion
**PR:** #146 | **Last activity:** 2024-02-23T22:24:20Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/146

The template no longer uses bumpversion

## #145: [docs] update readme badges and typos
**PR:** #145 | **Last activity:** 2024-02-23T22:12:07Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/145

## #143: [docs] add sphinx extlinks for changelog
**PR:** #143 | **Last activity:** 2024-02-23T21:50:50Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/143

## #142: [releases] start 0.5.1
**PR:** #142 | **Last activity:** 2024-02-23T21:28:23Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/142

## #141: [misc] add node_modules to ignore, put date on 0.5.0
**PR:** #141 | **Last activity:** 2024-02-23T21:09:20Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/141

## #140: [ci] remove prerelease flag from normal tests
**PR:** #140 | **Last activity:** 2024-02-23T21:01:05Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **URL:** https://github.com/YosefLab/scib-metrics/pull/140

## #134: Add prerelease, cuda, macos, windows test workflows
**PR:** #134 | **Last activity:** 2024-02-08T21:45:46Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-08 | **Labels:** all tests | **URL:** https://github.com/YosefLab/scib-metrics/pull/134

- Adds CUDA, macOS, and Windows test workflows that run on schedule, manually, or by adding appropriate labels to a PR
- Separates prerelease tests into its own workflow that runs on schedule

**@martinkim0:** Needs to rebase on #135

## #135: Replace deprecated `KeyArray` with `Array`
**PR:** #135 | **Last activity:** 2024-02-08T21:42:18Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-08 | **URL:** https://github.com/YosefLab/scib-metrics/pull/135

JAX 0.4.24 removed `random.KeyArray`. According to the deprecation warning, it can be replaced with `jax.Array`:
```
DeprecationWarning: jax.random.KeyArray is deprecated. Use jax.Array for annotations, and jax.dtypes.issubdtype(arr.dtype, jax.dtypes.prng_key) for runtime detection of typed prng keys (i.e. keys created with jax.random.key).
```

## #131: Create setup.py
**PR:** #131 | **Last activity:** 2024-01-05T14:58:04Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-01-05 | **URL:** https://github.com/YosefLab/scib-metrics/pull/131

## #130: Update release.yaml
**PR:** #130 | **Last activity:** 2024-01-04T18:37:01Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2024-01-04 | **URL:** https://github.com/YosefLab/scib-metrics/pull/130

## #125: Update template to v0.3.0
**PR:** #125 | **Last activity:** 2024-01-04T18:30:05Z
**State:** merged | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2023-11-28 | **URL:** https://github.com/YosefLab/scib-metrics/pull/125

`cookiecutter-scverse` released [v0.3.0](https://github.com/scverse/cookiecutter-scverse/releases/tag/v0.3.0).

## Changes

## Required actions

The Github `release` workflow has been updated to use [trusted publishing](https://docs.pypi.org/trusted-publishers/) for authentication. You'll need to configure your project on PyPI accordingly. See https://github.com/scverse/cookiecutter-scverse/issues/228 and [the PyPI documentation](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) for more details.

## Python version update

Python 3.11 now works with numba, so we increased the maximum tested version to Python 3.11.

## Enhancements

The automatic template sync is now in regular operation.

## Fixes

* Reduce font size in data frames (#250)
* Remove template usage docs from rendered template (now only available in `cookiecutter-scverse-instance` (#247)
* Remove sphinx setup function (#246)
* Move the section about how to configure the github release workflow to the template documentation (#248)
* Use `coverage run` instead of `pytest --cov` to compute test coverage (#244)
* Fix that the LICENSE file wasn't generated for GPL (#245)
* Fix socket warning in tests (#240)

If there are any questions, feel free to reach out to @grst, e.g. on the [scverse zulip](https://scverse.zulipchat.com).


## Additional remarks
* unsubscribe: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or, …

## #129: Refactor neighbors-based metrics to use `NeighborsResults`
**PR:** #129 | **Last activity:** 2024-01-04T17:32:06Z
**State:** merged | **Author:** @adamgayoso | **Comments:** 2 | **Created:** 2023-12-27 | **URL:** https://github.com/YosefLab/scib-metrics/pull/129

- Refactor neighbors-based metrics to use `NeighborsResults`, making it simpler for users as there is no confusion over passing distances or connectivities. Also reduces overhead of converting back and forth between sparse and dense representations of the neighbor results.
- Compute umap-based connectivities in this package instead of scanpy, and make the implementation more efficient
- Remove unnecessary vmap in pcr regression
- Update notebooks
- Drop usage of private scanpy functions. Scanpy can likely be dropped as a dependency in a future release if pca with implicit centering for sparse matrices makes it into sklearn
- Bump to 0.5.0

Fixes #109 as lisi always uses the dense (indices, distances) representation for neighbors. The issue arose when the approximate neighbors method gave a distance of zero to non-self cells.

**@jan-engelmann (review, approved):** LGTM!
Looked through and ran the tests.

Now for 500 000 cells the main time used is spent in `pynndescent` (86%) and in `fuzzy_simplical_set` (4%) see profiling results below. Also, tests are passing.  `test_kmeans` failed for me once locally but has been passing ever since.

Let me know if I should have a look at anything specific!

<details>

```python
K = 90
N = 500_000
Q = 30
X = np.random.randn(N, Q)
neigh_result = pynndescent(X, n_neighbors=K)
neigh_result = neigh_result.subset_neighbors(n=K)
new_connect = neigh_result.knn_graph_connectivities
new_dist = neigh_result.knn_graph_distances
```
  <summary>Profiling Results</summary>

![test_adam_profiled](https://github.com/YosefLab/scib-metrics/assets/43600842/4ab06294-6d35-4ac7-b635-d262b96179b3)
</details>

**@adamgayoso:** @jan-engelmann  thanks! I will make a release soon

## #128: Speedup `Benchmarker.prepare` (`compute_connectivities_umap`)
**PR:** #128 | **Last activity:** 2023-12-29T12:19:11Z
**State:** closed | **Author:** @jan-engelmann | **Comments:** 14 | **Created:** 2023-12-20 | **URL:** https://github.com/YosefLab/scib-metrics/pull/128

Thanks for the great package!

Unfortunately `Benchmarker.prepare()` is very slow due to currently released scanpy code:
`sc.neighbors._compute_connectivities_umap` is highly inefficient (see [this monster](https://github.com/scverse/scanpy/blob/1.9.6/scanpy/neighbors/__init__.py#L355)).

One iteration of the KNN calculation takes 2:30h for 7 Million cells. A large part of this time is spent in `sc.neighbors._compute_connectivities_umap`.

I see two solutions:
**A Use the approach proposed in this PR**
**B Use new scanpy code not yet released but already on main**

## A This PR
The solution in this PR offers the following speedup:
![image](https://github.com/YosefLab/scib-metrics/assets/43600842/d9282bf7-79b1-4bcb-b832-ec571da729ca)

## B Unreleased Scanpy code
The Neighbors scanpy code on main has been thoroughly refactored by @Zethson and likely offers a way to do this efficiently. For example `scanpy.neighbors._common._get_sparse_matrix_from_indices_distances` looks promising. I can look more into this if there's interest.

What do you think @Zethson @adamgayoso

**@Zethson:** I didn't touch the neighbors code. Maybe I merged a PR but that's about it.

I'd rather lobby for a new scanpy release and bring any improvements upstream into scanpy.

But cool work @jan-engelmann !

**@adamgayoso on `src/scib_metrics/utils/_utils.py`:** Please add typing

**@adamgayoso on `src/scib_metrics/utils/_utils.py`:** Can you put a more general docstring? Overview of the method and that it matches how connectivies are computed in scanpy?

**@adamgayoso on `src/scib_metrics/utils/_utils.py`:** nit: I prefer using keywords everywhere

**@adamgayoso on `tests/test_utils.py`:** nit: use `np.testing`

**@adamgayoso on `tests/test_utils.py`:** I don't think this test is necessary if you add a reproducible script to this PR description

**@adamgayoso on `src/scib_metrics/utils/_utils.py`:** is this bit still necessary? What's the lower bound for scanpy? If we merge this PR we will need to make umap a direct dependency, so please also add that and potentially remove this block.

**@adamgayoso (review, commented):** Thanks for this! I think this should be added to the package so we don't rely on a private fn of scanpy. Also the fn is quite simple.

**@adamgayoso:** Actually I would hold off on this PR. I see some redundancies in converting back and forth from sparse distance matrices that I'd like to address first. This should eliminate the need for building the sparse distance graph here

**@adamgayoso:** @jan-engelmann feel free to give a review to #129

**@adamgayoso:** Closed due to #129

@jan-engelmann I will add you as an author on the PR

**@jan-engelmann:** > But cool work @jan-engelmann !

thanks @Zethson  :)

**@jan-engelmann:** > Closed due to #129
>
> @jan-engelmann I will add you as an author on the PR

Thanks @adamgayoso I appreciate it! I like the refactoring. Very clean! 👍
Left a review on #129 but did not request any changes.

**@jan-engelmann:** Also thanks for the review! @adamgayoso
Will keep these things in mind for the next time
