#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Buildkite reports status on the requested SHA. Reject a stale checkout.
if [[ -n "${BUILDKITE_COMMIT:-}" && "${BUILDKITE_COMMIT}" != HEAD ]]; then
  test "$(git rev-parse HEAD)" = "$BUILDKITE_COMMIT"
fi
# Match GitHub Actions pull_request semantics: test GitHub's merge commit,
# but only when its second parent is exactly the requested PR head.
if [[ "${BUILDKITE_PULL_REQUEST:-false}" != false ]]; then
  [[ "$BUILDKITE_PULL_REQUEST" =~ ^[0-9]+$ ]]
  git fetch --no-tags origin "refs/pull/$BUILDKITE_PULL_REQUEST/merge"
  test "$(git rev-parse FETCH_HEAD^2)" = "$BUILDKITE_COMMIT"
  git checkout --detach FETCH_HEAD
fi
printf 'Verified source commit: %s\n' "$(git rev-parse HEAD)"
export COMPOSE_ANSI=never COMPOSE_PROGRESS=plain COMPOSE_MENU=false
export COMPOSE_PROJECT_NAME="ci-fakegreg-${BUILDKITE_JOB_ID:-local}"
cleanup() {
  result=$?
  set +e
  if (( result != 0 )); then
    container=$(docker compose -f .buildkite/compose.yml ps -aq verify)
    if [[ -n "$container" ]]; then
      mkdir -p .buildkite-artifacts
      for report in playwright-report test-results; do
        docker cp "$container:/workspace/$report" .buildkite-artifacts/ || true
      done
      if [[ -n "${BUILDKITE:-}" ]]; then
        buildkite-agent artifact upload '.buildkite-artifacts/**/*' || true
      fi
    fi
  fi
  docker compose -f .buildkite/compose.yml down --volumes --remove-orphans
  cleanup_result=$?
  if (( result == 0 && cleanup_result != 0 )); then result=$cleanup_result; fi
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
docker compose -f .buildkite/compose.yml up --build --abort-on-container-exit --exit-code-from verify
