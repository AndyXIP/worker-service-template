# CI

`.github/workflows/_core.yml` (called by both `ci.yml` on push to `main` and
`pr.yml` on pull requests) runs three jobs: `mise run check`, `mise run test`,
and `mise run build` followed by a Trivy vulnerability scan (fails the job on
any `HIGH`/`CRITICAL` CVE with a known fix) and a smoke test (`docker run` +
curl `/utils/health`).

`ci.yml` also calls `deploy.yml` with `needs: core`, so it only runs on push
to `main` and only after `core` passes. `pr.yml` does not call it, so PRs
never trigger a deploy attempt.

`deploy.yml` is a single reusable job parameterized by an `environment`
input, rather than one job per target:

- Auto path: `ci.yml` calls it via `workflow_call` with
  `environment: development`, so every push to `main` that passes `core`
  deploys to the `development` GitHub Environment automatically.
- Manual path: `workflow_dispatch` ("Run workflow" in the Actions tab) offers
  only `production` as a choice, so prod deploys always require an explicit
  manual trigger — there's no automatic path to `production`. The `deploy`
  job's `if` guards this path to `github.ref == 'refs/heads/main'`, so a
  manual dispatch against any other branch is skipped — prod can only ever
  deploy what's on `main`.

A `concurrency` group keyed by `environment` (`cancel-in-progress: false`)
means a second deploy to the same environment queues behind an in-flight one
instead of racing it or cancelling it mid-deploy.

The job's `environment: name: ${{ inputs.environment }}` picks up whichever
value came in, so the same steps run against either target. The `Deploy`
step is currently an `echo` placeholder — the trigger/gating and Environment
wiring are real and don't need touching, only the `run:` block needs
replacing with an actual deploy command once there's a real target (it can
branch on `inputs.environment` if dev/prod need different commands).
Consider adding required reviewers on the `production` Environment (repo
Settings > Environments) to gate manual prod deploys.
