# Releasing

Publishing to PyPI goes through
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC, no API token), and
[release.yml](.github/workflows/release.yml) runs it on every push of a `v*` tag.

## One-time PyPI setup

1. Sign in to PyPI and register the following from
   [Publishing](https://pypi.org/manage/account/publishing/)
   under "Add a new pending publisher":
   - PyPI Project Name: `gettext-tstrings`
   - Owner: `yhay81`
   - Repository name: `gettext-tstrings`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
2. Create a `pypi` environment under Settings → Environments in the GitHub
   repository (protection rules are optional).

## Every release

1. Bump `__version__` in `src/gettext_tstrings/__init__.py`
   (pyproject.toml declares a dynamic version that reads it from there).
2. Rename `## Unreleased` in `CHANGELOG.md` to the new version number and date.
3. Commit, push to main, and confirm CI is green.
4. Tag and push (the workflow verifies that the tag matches the version):

   ```console
   git tag v0.1.0a2
   git push origin v0.1.0a2
   ```

5. Confirm the workflow completes (CI-equivalent checks → build → wheel smoke
   test → PyPI publish), then create a GitHub Release from the tag and paste in
   the matching CHANGELOG section.
6. Verify `pip install gettext-tstrings` in a clean environment.
