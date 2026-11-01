# YosefLab/scvi-hub-models GitHub Issues Q&A

1 issues (open and closed, bots excluded) from YosefLab/scvi-hub-models with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; issues are only removed once they age out of that window.

## #4: Idea board for how model uploads should run here
**Issue:** #4 | **Last activity:** 2024-02-01T23:23:41Z
**State:** open | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-01 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scvi-hub-models/issues/4

Necessary:

- Model upload workflows should run for every release of scvi-tools with appropriate revision tags

Nice to have:

- "Dry runs" of upload workflows with nightly or weekly scvi-tools to make sure newest changes are compatible
- "Mirrors" of tutorial models so that users have the option to set a (non-default) flag on the top of their notebooks to just use the pre-trained model instead of training themselves
- Tensorboard logs instead of storing losses in the model itself for easier viewing
- PPC metrics and/or integration metrics pre-computed

Not sure about:

- Whether we should have backport branches

Implementation:

- Workflows most likely have to run on self-hosted runners due to RAM limits and GPU acceleration for the subset of models that are trained on our end
- Need a new Docker image tag for these workflows
- We should be able to pass in revision tags as an argument to the workflow
