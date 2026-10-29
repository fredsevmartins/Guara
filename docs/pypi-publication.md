# Optional PyPI publication using Trusted Publishing

The wheel and sdist are built and checked locally/CI. A prepared workflow is not proof that a
package exists on PyPI. During v0.1.2 preparation, the public JSON endpoint for `opentruth` returned
404 and no publishing credentials/bindings were available in the cloud environment. A 404 does
not reserve a project name or grant ownership. GitHub API access was also blocked by the proxy.

An authorized maintainer must configure PyPI and GitHub before publication:

1. Sign into the maintainer's PyPI account. For a new project, create a pending Trusted Publisher
   for project `opentruth`, GitHub owner `fredsevmartins`, repository `OpenTruth`, workflow filename
   `publish-pypi.yml`, and environment `pypi`. If the name is already owned, resolve project access;
   do not publish under an unrelated owner or silently rename the package.
2. Create the GitHub repository environment `pypi` and restrict it to authorized release reviewers
   and approved tags. Set required reviewers when available for the repository plan.
3. Confirm the version's Linux/macOS/Windows CI and GitHub Release. Then manually dispatch
   **Publish to PyPI (manual)** with the existing tag (for example `v0.1.2`).
4. Review/approve the `pypi` environment deployment. The validation job checks out that exact tag,
   confirms its package version, runs tests/tutorial/lint, builds and checks metadata, and installs
   the wheel independently. A separate job downloads only those artifacts and uses OIDC; no long-lived
   API key is stored in the repository. The publish job alone has `id-token: write`.
5. Verify the resulting PyPI release/files and perform a fresh registry installation before
   documenting `pip install opentruth` as an available installation path. Release numbers cannot be
   overwritten on PyPI. Do not move a published tag or skip checks to work around a failed upload.

The workflow is manual, not triggered automatically by tags or GitHub Releases. Source installation
remains the verified documented path until an actual registry publication has been confirmed.
