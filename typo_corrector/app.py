from functools import partial
import json
from logging import getLogger, Logger
import time

from pynput import keyboard

from .clipboard_manager import ClipboardManager
from .config import save_config, load_config, CONFIG_PATH
from .llm_agent import LLMAgent
from .ui import TkinterUserInterface, EConfirmation
from .utils import create_hotkey_str, pipeline


class App:

    WAIT_TIME: float = 0.5

    def __init__(
        self,
        llm_agent: LLMAgent,
        user_interface: TkinterUserInterface,
        clipboard_manager: ClipboardManager,
        config_path: str = CONFIG_PATH,
        logger: Logger = getLogger(__name__),
    ):
        self.llm_agent = llm_agent
        self.user_interface = user_interface
        self.clipboard_manager = clipboard_manager
        self.config = None
        self.keybinds = None
        self.config_path = config_path
        self.logger = logger

    def prepare(self):
        self.logger.info('Preparing the application...')

        # load config
        self.config = load_config(self.config_path)
        self.logger.info(f'config: {json.dumps(self.config.model_dump())}')

        # prepare keybinds
        self.keybinds = keyboard.GlobalHotKeys({
            create_hotkey_str(**self.config.config_keybind.model_dump()): self.change_config,  # noqa
            create_hotkey_str(**self.config.activation_keybind.model_dump()): self.correct_selected_text,  # noqa
        })

        # prepare
        self.user_interface.prepare()
        self.logger.info('Preparation has been completed')

    def start(self):
        self.logger.info(f'{self.__class__.__name__}.start has been called')
        assert self.keybinds is not None
        self.keybinds.start()

        self.logger.info(f'{self.__class__.__name__}.start has been completed')
        self.user_interface.start()

    def end(self):
        self.logger.info(f'{self.__class__.__name__}.end has been called')
        self.keybinds.stop()
        self.user_interface.end()
        if self.keybinds.is_alive():
            del self.keybinds
        assert not self.user_interface.activated
        self.config = None
        self.keybinds = None
        self.logger.info(f'{self.__class__.__name__}.end has been completed')

    def restart(self):
        self.logger.info(f'{self.__class__.__name__}.restart has been called')
        self.end()
        self.prepare()
        self.start()

    def change_config(self):
        self.logger.info(f'{self.__class__.__name__}.change_config has been called')  # noqa
        self.user_interface.show_config(
            current_config=self.config,
            callback=pipeline(
                partial(save_config, config_path=self.config_path),
                lambda *args, **kwargs: self.restart(),
            )
        )

    def correct_selected_text(self):
        self.logger.info(f'{self.__class__.__name__}.correct_selected_text has been called')  # noqa

        # get the copied text
        copied_text = self.clipboard_manager.copy_selected2clipboard()
        self.logger.debug(f'copied_text: {copied_text}')

        # correct the text
        corrected_text = self.llm_agent.interact(
            pairs_of_header_body=[
                ('', 'You are a world-class proofreader of texts. You can work with multiple languages. We are now presenting you with constraints, example proofreading procedures, and input text. Please follow the given procedure to proofread the input text, following the examples and adhering to the constraints.'),  # noqa
                ('Follow the following rules which you have to follow:', self.config.condition_str),  # noqa
                ('Examples:', self.config.example_str),  # noqa
                ('Procedures:', '1. detect the language of the input sentence (e.g. Hello -> English);\n2. detect errors (typos, omissions, etc.) in the input text and list them as bullet points;\n3. correct input sentences by referring to constraints and examples'),  # noqa
                ('Here is the input text which you should correct:', copied_text),  # noqa
                ('', '''Finally, the format of the output must be as f,ollows

==========START==========
### 1 ###
{result of procedure 1}

### 2 ###
{result of procedure 2}

### 3 ###
{result of procedure 3}
===========END===========''')
            ],
            callback=lambda x: x.split('==========START==========')[-1]  \
                                .split('===========END===========')[0]  \
                                .split('### 3 ###')[-1]  \
                                .strip(),
        )
        self.logger.debug(f'corrected_text: {corrected_text}')

        def callback(confirmation: EConfirmation):
            # copy the corrected text into clipboard
            self.clipboard_manager.copy_py2clipboard(corrected_text)
            # paste the corrected text from clipboard
            if confirmation == EConfirmation.YES:
                self.clipboard_manager.paste_from_clipboard()
            self.logger.info("Correcting text has been completed")

        self.user_interface.show_confirmation(
            text_before=copied_text,
            text_after=corrected_text,
            callback=callback,
        )
