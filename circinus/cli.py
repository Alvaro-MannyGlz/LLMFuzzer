from pathlib import Path

import click

from circinus.afl_pipeline import AFLRunConfig, run_afl
from circinus.fuzzer import UserInput, candidate_prompt, fuzzing_loop
from circinus.llm import GPT
from circinus.seed_cache import (
    crash_artifacts_to_cached_seeds,
    hydrate_seed_directory,
    load_seed_cache,
    save_seed_cache,
)
from circinus.settings import load_config
from circinus.vulnerability_reporter import (
    OllamaVulnerabilityReporter,
    collect_crash_artifacts,
    write_markdown_report,
)


def _default_config_path() -> Path:
    notebook_config = Path('notebook/conf.toml')
    if notebook_config.exists():
        return notebook_config
    return Path('conf.toml')


@click.command()
@click.option(
    '-d', '--documentation',
    type=click.Path(dir_okay=False, resolve_path=True),
    help='',
)
@click.option(
    '-sp', '--specification',
    type=click.Path(dir_okay=False, resolve_path=True),
    help='',
)
@click.option(
    '-c', '--code',
    type=click.Path(dir_okay=False, resolve_path=True),
    help='',
)
@click.option(
    '-s', '--samples',
    type=int,
    default=2,
    help='',
)
@click.option(
    '-o', '--output',
    type=click.Path(file_okay=False, resolve_path=True),
    help='Output directory.'
)
@click.option(
    '--config',
    type=click.Path(dir_okay=False, resolve_path=True),
    default=str(_default_config_path()),
    show_default=True,
    help='Path to Dynaconf TOML config file.',
)
@click.option(
    '--seed-cache',
    type=click.Path(dir_okay=False, resolve_path=True),
    default='.circinus-seed-cache.json',
    show_default=True,
    help='JSON file used to persist crash-derived seeds between runs.',
)
@click.option(
    '--afl',
    is_flag=True,
    default=False,
    help='Launch AFL++ using generated Circinus seeds.',
)
@click.option(
    '--afl-binary',
    default='afl-fuzz',
    show_default=True,
    help='AFL++ executable path.',
)
@click.option(
    '--afl-target-cmd',
    default=None,
    help='Target command passed after "--" to afl-fuzz (use @@ placeholder for input files).',
)
@click.option(
    '--afl-output-dir',
    type=click.Path(file_okay=False, resolve_path=True),
    default=None,
    help='AFL++ findings output directory.',
)
@click.option(
    '--afl-extra-args',
    multiple=True,
    help='Extra afl-fuzz arguments (repeatable).',
)
@click.option(
    '--afl-timeout',
    type=int,
    default=None,
    help='Optional timeout in seconds for the afl-fuzz command.',
)
@click.option(
    '--crash-data',
    type=click.Path(exists=True, resolve_path=True),
    default=None,
    help='Crash file or directory to summarize into a vulnerability report.',
)
@click.option(
    '--vuln-report',
    type=click.Path(dir_okay=False, resolve_path=True),
    default=None,
    help='Output markdown report path for crash analysis.',
)
@click.option(
    '--ollama-model',
    default='llama3.1',
    show_default=True,
    help='Ollama model name for vulnerability reporting.',
)
@click.option(
    '--ollama-base-url',
    default='http://localhost:11434/v1',
    show_default=True,
    help='OpenAI-compatible Ollama base URL.',
)
def cli(
    documentation: str,
    specification: str,
    code: str,
    samples: int,
    output: str,
    config: str,
    seed_cache: str,
    afl: bool,
    afl_binary: str,
    afl_target_cmd: str | None,
    afl_output_dir: str | None,
    afl_extra_args: tuple[str, ...],
    afl_timeout: int | None,
    crash_data: str | None,
    vuln_report: str | None,
    ollama_model: str,
    ollama_base_url: str,
) -> None:
    load_config(config)
    llm = GPT()
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    seed_cache_path = Path(seed_cache)

    cached_seeds = load_seed_cache(seed_cache_path)
    if cached_seeds:
        hydrate_seed_directory(output_path, cached_seeds)

    prompts = candidate_prompt(
        llm=llm,
        user_input=UserInput(
            documentation=Path(documentation).read_text(encoding='utf-8'),
            specification=Path(specification).read_text(encoding='utf-8'),
            code=Path(code).read_text(encoding='utf-8')
        ),
        num_samples=samples,
    )

    crash_artifacts = []
    generated_files: list[Path] = []
    for index_x, prompt in enumerate(prompts):
        snippets = fuzzing_loop(llm=llm, prompt=prompt)
        for index_y, snippet in enumerate(snippets):
            if snippet:
                snippet_path = output_path / f'{index_x}-{index_y}.txt'
                snippet_path.write_text(data=snippet, encoding='utf-8')
                generated_files.append(snippet_path)

    if afl:
        if not afl_target_cmd:
            raise click.ClickException('--afl requires --afl-target-cmd.')

        afl_results_dir = Path(afl_output_dir) if afl_output_dir else (output_path / 'afl_results')
        run_afl(
            config=AFLRunConfig(
                afl_binary=afl_binary,
                input_dir=output_path,
                output_dir=afl_results_dir,
                target_command=afl_target_cmd,
                extra_args=tuple(afl_extra_args),
            ),
            timeout=afl_timeout,
        )
        click.echo(f'Launched AFL++ with {len(generated_files)} generated seeds. Results in: {afl_results_dir}')

        crash_dirs = [path for path in afl_results_dir.rglob('crashes') if path.is_dir()]
        for crash_dir in crash_dirs:
            crash_artifacts.extend(collect_crash_artifacts(crash_dir))

    if crash_data:
        crash_artifacts.extend(collect_crash_artifacts(Path(crash_data)))

    if crash_artifacts:
        cached_seed_entries = crash_artifacts_to_cached_seeds(crash_artifacts)
        save_seed_cache(seed_cache_path, cached_seed_entries)

    if crash_data:
        if not crash_artifacts:
            raise click.ClickException(f'No crash artifacts found in: {crash_data}')

        reporter = OllamaVulnerabilityReporter(model=ollama_model, base_url=ollama_base_url)
        target = afl_target_cmd or 'unspecified-target'
        report_body = reporter.generate_report(target=target, artifacts=crash_artifacts)

        report_path = Path(vuln_report) if vuln_report else (output_path / 'vulnerability_report.md')
        write_markdown_report(report_path=report_path, target=target, report_body=report_body)
        click.echo(f'Wrote vulnerability report: {report_path}')
