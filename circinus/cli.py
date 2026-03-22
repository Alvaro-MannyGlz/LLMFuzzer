from pathlib import Path

import click

from circinus.fuzzer import UserInput, candidate_prompt, fuzzing_loop
from circinus.llm import GPT
from circinus.settings import load_config


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
def cli(documentation: str, specification: str, code: str, samples: int, output: str, config: str) -> None:
    load_config(config)
    llm = GPT()

    prompts = candidate_prompt(
        llm=llm,
        user_input=UserInput(
            documentation=Path(documentation).read_text(encoding='utf-8'),
            specification=Path(specification).read_text(encoding='utf-8'),
            code=Path(code).read_text(encoding='utf-8')
        ),
        num_samples=samples,
    )

    for index_x, prompt in enumerate(prompts):
        snippets = fuzzing_loop(llm=llm, prompt=prompt)
        for index_y, snippet in enumerate(snippets):
            if snippet:
                (Path(output) / f'{index_x}-{index_y}.txt').write_text(data=snippet, encoding='utf-8')
