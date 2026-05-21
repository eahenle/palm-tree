from publishing.github_utils import (
    compute_diff_sha,
    get_repo,
    save_pr_to_local,
    should_skip_review,
    update_cached_sha,
)


def test_compute_diff_sha_consistency():
    diff = "file.md:\n- old\n+ new"
    sha1 = compute_diff_sha(diff)
    sha2 = compute_diff_sha(diff)
    assert sha1 == sha2


def test_should_skip_review(tmp_path, monkeypatch):
    # Fake SHA DB
    test_sha = "abc123"
    pr_number = 42
    cache_file = tmp_path / "pr_shas.json"
    cache_file.write_text(f'{{"{pr_number}": "{test_sha}"}}')

    monkeypatch.setattr("publishing.github_utils.PR_SHAS_FILE", cache_file)

    assert should_skip_review(pr_number, "abc123")
    assert not should_skip_review(pr_number, "xyz789")


def test_update_cached_sha_roundtrip(tmp_path, monkeypatch):
    pr_number = 100
    sha = "def456"
    cache_file = tmp_path / "pr_shas.json"
    monkeypatch.setattr("publishing.github_utils.PR_SHAS_FILE", cache_file)

    update_cached_sha(pr_number, sha)
    try:
        assert should_skip_review(pr_number, sha)
    finally:
        if cache_file.exists():
            cache_file.unlink()


def test_get_repo_raises_when_unconfigured(monkeypatch):
    monkeypatch.setattr("publishing.github_utils.REPO", None)

    try:
        get_repo()
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "GitHub repo is not configured" in str(exc)


def test_save_pr_to_local_writes_expected_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    context_path = tmp_path / "last_pr.txt"
    monkeypatch.setattr("publishing.github_utils.PR_CONTEXT_FILE", str(context_path))

    output_dir = save_pr_to_local(7, "diff body", "comment body")

    assert (tmp_path / output_dir / "diff.md").exists()
    assert (tmp_path / output_dir / "comments.md").exists()
    assert context_path.read_text() == "7"
