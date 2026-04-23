import os
from pathlib import Path

from circinus.settings import load_config


def test_load_config_reads_env_file_without_toml(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / '.env'
    env_file.write_text('LLM_MODEL=unit-test-model\n', encoding='utf-8')

    monkeypatch.delenv('LLM_MODEL', raising=False)

    load_config(tmp_path / 'missing.toml')

    assert os.environ['LLM_MODEL'] == 'unit-test-model'