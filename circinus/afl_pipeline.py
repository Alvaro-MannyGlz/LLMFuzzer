import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AFLRunConfig:
    afl_binary: str
    input_dir: Path
    output_dir: Path
    target_command: str
    extra_args: tuple[str, ...] = ()


def build_afl_command(config: AFLRunConfig) -> list[str]:
    command = [
        config.afl_binary,
        '-i',
        str(config.input_dir),
        '-o',
        str(config.output_dir),
    ]
    command.extend(config.extra_args)
    command.append('--')
    command.extend(shlex.split(config.target_command, posix=(os.name != 'nt')))
    return command


def run_afl(config: AFLRunConfig, timeout: int | None = None) -> subprocess.Popen:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        build_afl_command(config),
        stdout=None,
        stderr=None,
    )
    if timeout is not None:
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return process
    return process