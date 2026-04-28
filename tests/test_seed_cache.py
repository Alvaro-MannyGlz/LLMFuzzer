from pathlib import Path

from circinus.seed_cache import (
    CachedSeed,
    crash_artifacts_to_cached_seeds,
    hydrate_seed_directory,
    load_seed_cache,
    save_seed_cache,
)
from circinus.vulnerability_reporter import CrashArtifact


def test_save_and_load_seed_cache_round_trip(tmp_path: Path) -> None:
    cache_path = tmp_path / 'seed-cache.json'
    seeds = [
        CachedSeed(source='crash-a', content='boom', content_hash='hash-a'),
        CachedSeed(source='crash-b', content='boom', content_hash='hash-a'),
    ]

    save_seed_cache(cache_path, seeds)
    loaded = load_seed_cache(cache_path)

    assert len(loaded) == 1
    assert loaded[0].content == 'boom'
    assert loaded[0].source == 'crash-a'


def test_hydrate_seed_directory_writes_files(tmp_path: Path) -> None:
    seed_dir = tmp_path / 'seeds'
    seeds = [CachedSeed(source='crash-a', content='seed-1', content_hash='hash-1')]

    written = hydrate_seed_directory(seed_dir, seeds)

    assert len(written) == 1
    assert written[0].read_text(encoding='utf-8') == 'seed-1'


def test_crash_artifacts_to_cached_seeds_uses_content_hash(tmp_path: Path) -> None:
    seeds = crash_artifacts_to_cached_seeds([
        CrashArtifact(source='crash', content='unique crash input'),
    ])

    assert len(seeds) == 1
    assert seeds[0].content == 'unique crash input'
    assert seeds[0].source == 'crash'