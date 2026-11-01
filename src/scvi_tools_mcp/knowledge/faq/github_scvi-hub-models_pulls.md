# YosefLab/scvi-hub-models GitHub Pull Requests

15 pull requests (open, closed and merged, bots excluded) from YosefLab/scvi-hub-models with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; PRs are only removed once they age out of that window.

## #18: Update template to v0.8.0
**PR:** #18 | **Last activity:** 2026-07-17T07:12:13Z
**State:** open | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2026-07-17 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/18

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

## #16: Update template to v0.7.0
**PR:** #16 | **Last activity:** 2026-07-17T07:12:11Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-12-24 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/16

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

## #17: fix: update hub scripts and models
**PR:** #17 | **Last activity:** 2026-03-01T11:01:55Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-02-26 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/17

## #15: Update template to v0.6.0
**PR:** #15 | **Last activity:** 2025-12-24T09:48:58Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-09-30 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/15

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

## #14: Update template to v0.5.0
**PR:** #14 | **Last activity:** 2025-09-30T06:23:33Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-04-02 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/14

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

## #13: Change file names.
**PR:** #13 | **Last activity:** 2024-12-13T04:43:11Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-13 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/13

## #12: AWS backup files
**PR:** #12 | **Last activity:** 2024-12-12T22:30:20Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-12 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/12

## #5: Update template to v0.3.1
**PR:** #5 | **Last activity:** 2024-12-12T06:06:53Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2024-02-22 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/5

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

## #8: Revision2
**PR:** #8 | **Last activity:** 2024-12-12T06:01:12Z
**State:** closed | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-10 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/8

Updates.

## #11: Revision3
**PR:** #11 | **Last activity:** 2024-12-12T06:00:33Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-12 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/11

## #10: Revision3
**PR:** #10 | **Last activity:** 2024-12-10T08:19:09Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-10 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/10

## #9: Revision3
**PR:** #9 | **Last activity:** 2024-12-10T07:26:41Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-10 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/9

## #7: Revision
**PR:** #7 | **Last activity:** 2024-12-10T05:55:58Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-10 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/7

## #6: Revision
**PR:** #6 | **Last activity:** 2024-12-06T19:20:35Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-12-06 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/6

## #3: Update template to v0.3.0
**PR:** #3 | **Last activity:** 2024-02-01T20:29:25Z
**State:** merged | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2023-11-28 | **URL:** https://github.com/YosefLab/scvi-hub-models/pull/3

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
