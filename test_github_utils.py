from github_utils import compute_diff_sha, should_skip_review, update_cached_sha

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

    monkeypatch.setattr("github_utils.PR_SHAS_FILE", cache_file)

    assert should_skip_review(pr_number, "abc123")
    assert not should_skip_review(pr_number, "xyz789")

def test_update_cached_sha_roundtrip(tmp_path, monkeypatch):
    pr_number = 100
    sha = "def456"
    cache_file = tmp_path / "pr_shas.json"
    monkeypatch.setattr("agentic_blog_bot.github_utils.PR_SHAS_FILE", cache_file)

    update_cached_sha(pr_number, sha)
    try:
        assert should_skip_review(pr_number, sha)
    finally:
        if cache_file.exists():
            cache_file.unlink()
