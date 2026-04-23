from pathlib import Path
import os

import dynaconf


settings = dynaconf.Dynaconf(environments=False)


def _load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[len('export '):].strip()
        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(config_file: Path | str) -> dynaconf.Dynaconf:
    config_path = Path(config_file).resolve()
    _load_env_file(config_path.parent / '.env')
    _load_env_file(Path(__file__).resolve().parent.parent / '.env')
    if config_path.exists():
        settings.load_file(path=str(config_path))
    return settings
