# Buildkite verification

Run `.buildkite/verify.sh` with Docker and Compose to execute the same complete gate
used by Buildkite. Build/test commands live in `.buildkite/run.sh`. PR builds require
the exact requested head and verify GitHub's matching merge ref. The shared Linux
queue has independent Cachy and ThinkPad runners; both accept only trusted repository
sources. Fork builds are disabled.

The container receives source files and synthetic test data, with no developer env
files or agent/checkout credentials. Compose services, networks, and volumes are
removed on success, failure, or cancellation. Any available browser failure reports
are uploaded through Buildkite and retained for the organization's 30-day period.

Buildkite replaces GitHub Actions for this repository. The replacement PR suite
was verified before removing the workflows. Repository Actions is disabled only
after the merged default-branch build also passes. Historical Git branches remain intact.

## Dependency refresh

Python 3.12 standard-library verification needs no third-party dependency refresh.
