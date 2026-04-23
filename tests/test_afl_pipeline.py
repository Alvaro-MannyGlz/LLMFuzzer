from pathlib import Path

from circinus.afl_pipeline import AFLRunConfig, build_afl_command


def test_build_afl_command_contains_seed_handoff_and_target() -> None:
    config = AFLRunConfig(
        afl_binary='afl-fuzz',
        input_dir=Path('seeds'),
        output_dir=Path('findings'),
        target_command='python target.py @@',
        extra_args=('-m', 'none'),
    )

    command = build_afl_command(config)

    assert command[0] == 'afl-fuzz'
    assert '-i' in command
    assert 'seeds' in command
    assert '-o' in command
    assert 'findings' in command
    assert '--' in command
    assert 'python' in command
    assert '@@' in command