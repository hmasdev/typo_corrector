import json
from logging import getLogger, Logger
import os

import pydantic
from pydantic import BaseModel
if pydantic.__version__ >= '2.0.0':
    from pydantic import field_validator
else:
    from pydantic import validator as field_validator   # type: ignore


# path
CONFIG_DIR: str = os.path.join(os.path.expanduser('~'), '.typo_corrector')
CONFIG_PATH: str = os.path.join(CONFIG_DIR, 'config.json')
os.makedirs(CONFIG_DIR, exist_ok=True)


class Keybind(BaseModel):

    use_ctrl: bool
    use_alt: bool
    use_shift: bool
    use_super: bool
    char: str

    @field_validator('char')
    @classmethod
    def check_char(cls, char: str) -> str:
        assert isinstance(char, str)
        assert len(char) == 1
        return char


class Config(BaseModel):

    # keybind
    activation_keybind: Keybind
    config_keybind: Keybind

    # assumptions in LLM input
    condition_str: str
    example_str: str


# default config
DEFAULT_CONFIG = Config(
        activation_keybind=Keybind(use_ctrl=True, use_alt=True, use_shift=True, use_super=False, char='b'),  # noqa
        config_keybind=Keybind(use_ctrl=True, use_alt=True, use_shift=True, use_super=False, char='v'),  # noqa
        condition_str="""- Changes should be as minimal as possible;
- Do not change the main idea of the text.
        """,
        example_str="""- Helo world! -> Hello world!
- maintanance -> maintenance
        """
)


def save_config(
    config: Config,
    config_path: str = CONFIG_PATH,
    logger: Logger = getLogger(__name__),
):
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.model_dump(), f, indent=4, ensure_ascii=False)
        logger.info(f'Config has been saved to {config_path}')


def load_config(
    config_path: str = CONFIG_PATH,
    default_config: Config = DEFAULT_CONFIG,
    logger: Logger = getLogger(__name__),
) -> Config:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = Config(**json.load(f))
            logger.info(f'Config has been loaded from {config_path}')
        return config
    except FileNotFoundError:
        logger.warning(
            f'Config file not found: {config_path}. '
            f'So created a new config file: {default_config}',
        )
        save_config(default_config, config_path=config_path)
        return default_config
