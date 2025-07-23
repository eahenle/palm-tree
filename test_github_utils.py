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
