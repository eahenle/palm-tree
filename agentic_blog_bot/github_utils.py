import json
import hashlib
from pathlib import Path

# Minimal implementations for tests
CACHE_PATH = Path('.agent_cache')
CACHE_PATH.mkdir(exist_ok=True)
PR_SHAS_FILE = CACHE_PATH / 'pr_shas.json'


def get_cached_shas():
    if PR_SHAS_FILE.exists():
        with open(PR_SHAS_FILE) as f:
            return json.load(f)
    return {}

def update_cached_sha(pr_number: int, sha: str):
    shas = get_cached_shas()
    shas[str(pr_number)] = sha
    with open(PR_SHAS_FILE, 'w') as f:
        json.dump(shas, f)

def compute_diff_sha(diff_text: str) -> str:
    return hashlib.sha256(diff_text.encode()).hexdigest()

def should_skip_review(pr_number: int, new_sha: str) -> bool:
    shas = get_cached_shas()
    return shas.get(str(pr_number)) == new_sha
