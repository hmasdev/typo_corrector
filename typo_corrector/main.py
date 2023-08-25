from logging import basicConfig, DEBUG, getLogger, Logger, INFO  # noqa
import os

from langchain.llms import OpenAI

from .app import App
from .clipboard_manager import ClipboardManager
from .config import CONFIG_PATH
from .keyboard_manager import KeyboardManager
from .llm_agent import LLMAgent
from .ui import TkinterUserInterface

basicConfig(
    level=INFO,
    format="%(asctime)s - %(levelname)s - [File: %(filename)s:%(lineno)d, Thread: %(thread)d] - %(message)s"  # noqa
)


def main(logger: Logger = getLogger(__name__)):

    app = App(
        llm_agent=LLMAgent(llm=OpenAI(openai_api_key=os.environ['OPENAI_API_KEY'])),  # noqa
        user_interface=TkinterUserInterface(keyboard_manager=KeyboardManager()),  # noqa
        clipboard_manager=ClipboardManager(keyboard_manager=KeyboardManager()),  # noqa
        config_path=CONFIG_PATH,
    )
    logger.debug('App has been created')

    app.prepare()
    logger.debug('App has been prepared')

    app.start()


if __name__ == '__main__':
    main()
