# リリース手順

PyPIへの公開は[Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(APIトークン不要のOIDC)で、`v*` タグのpushをトリガーに
[release.yml](.github/workflows/release.yml)が実行する。

## 初回のみ: PyPI側の設定

1. PyPIにログインし、[Publishing](https://pypi.org/manage/account/publishing/)
   から "Add a new pending publisher" で以下を登録する:
   - PyPI Project Name: `gettext-tstrings`
   - Owner: `yhay81`
   - Repository name: `gettext-tstrings`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
2. GitHubリポジトリの Settings → Environments で `pypi` environmentを作成する
   (保護ルールは任意)。

## 毎回のリリース

1. `src/gettext_tstrings/__init__.py` の `__version__` を上げる
   (pyproject.tomlはdynamic versionでここを参照する)。
2. `CHANGELOG.md` の `## Unreleased` を新しいバージョン番号と日付に付け替える。
3. コミットしてmainへpushし、CIが緑であることを確認する。
4. タグを打ってpushする(タグとバージョンの一致はworkflowが検証する):

   ```console
   git tag v0.1.0a2
   git push origin v0.1.0a2
   ```

5. workflowの完了(build → wheelのsmoke test → PyPI publish)を確認し、
   タグからGitHub Releaseを作成してCHANGELOGの該当節を貼る。
6. クリーンな環境で `pip install gettext-tstrings` を確認する。
