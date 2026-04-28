from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from .vulnerability_reporter import CrashArtifact


@dataclass(frozen=True)
class CachedSeed:
    source: str
    content: str
    content_hash: str
    kind: str = 'crash'


def _seed_hash(content: str) -> str:
    return sha256(content.encode('utf-8')).hexdigest()


def _normalize_cached_seed(entry: dict) -> CachedSeed | None:
    content = str(entry.get('content', '')).strip()
    if not content:
        return None

    source = str(entry.get('source', 'unknown'))
    content_hash = str(entry.get('content_hash') or _seed_hash(content))
    kind = str(entry.get('kind', 'crash'))
    return CachedSeed(source=source, content=content, content_hash=content_hash, kind=kind)


def load_seed_cache(cache_path: Path) -> list[CachedSeed]:
    if not cache_path.exists():
        return []

    raw_data = json.loads(cache_path.read_text(encoding='utf-8'))
    entries = raw_data.get('seeds', []) if isinstance(raw_data, dict) else raw_data

    seeds: list[CachedSeed] = []
    seen_hashes: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        seed = _normalize_cached_seed(entry)
        if seed is None or seed.content_hash in seen_hashes:
            continue
        seen_hashes.add(seed.content_hash)
        seeds.append(seed)
    return seeds


def save_seed_cache(cache_path: Path, seeds: list[CachedSeed]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    unique_seeds: list[CachedSeed] = []
    seen_hashes: set[str] = set()
    for seed in seeds:
        if seed.content_hash in seen_hashes:
            continue
        seen_hashes.add(seed.content_hash)
        unique_seeds.append(seed)

    cache_path.write_text(
        json.dumps(
            {
                'version': 1,
                'generated_utc': datetime.now(timezone.utc).isoformat(),
                'seeds': [asdict(seed) for seed in unique_seeds],
            },
            indent=2,
        ),
        encoding='utf-8',
    )


def crash_artifacts_to_cached_seeds(artifacts: list[CrashArtifact]) -> list[CachedSeed]:
    seeds: list[CachedSeed] = []
    for artifact in artifacts:
        content = artifact.content.strip()
        if not content:
            continue
        seeds.append(
            CachedSeed(
                source=artifact.source,
                content=content,
                content_hash=_seed_hash(content),
            )
        )
    return seeds


def hydrate_seed_directory(seed_dir: Path, seeds: list[CachedSeed], prefix: str = 'cached') -> list[Path]:
    seed_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[Path] = []
    for index, seed in enumerate(seeds):
        file_path = seed_dir / f'{prefix}-{index:04d}.txt'
        file_path.write_text(seed.content, encoding='utf-8')
        written_files.append(file_path)
    return written_files
