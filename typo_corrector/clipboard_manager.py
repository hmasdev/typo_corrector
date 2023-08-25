from logging import getLogger, Logger
import time

import pyperclip

from .keyboard_manager import KeyboardManager


class ClipboardManager:

    def __init__(
        self,
        wait_time: float = 0.5,
        retry: int = 10,
        keyboard_manager: KeyboardManager = KeyboardManager(),
        logger: Logger = getLogger(__name__),
    ):
        self.wait_time = wait_time
        self.retry = retry
        self.keyboard_manager = keyboard_manager
        self.logger = logger

    def copy_py2clipboard(self, text: str):
        self.logger.info(f'Copying {text} to clipboard')
        pyperclip.copy(text)

    def copy_clipboard2py(self) -> str:
        self.logger.info('Copying from clipboard')
        return pyperclip.paste()

    def copy_selected2clipboard(self) -> str:
        self.logger.info('Copying selected text to clipboard')
        previous_clipboard = pyperclip.paste()
        for itr in range(self.retry):
            self.keyboard_manager.copy()
            time.sleep(self.wait_time)
            if previous_clipboard != pyperclip.paste():
                break
            self.logger.warning(
                'The selected text may not be copied into clipboard '
                'because the clipboard is not changed. '
                f'Try AGAIN. ({itr+1} / {self.retry})')  # noqa
        else:
            self.logger.warning('The selected text may not be copied into clipboard because the clipboard is not changed')  # noqa

        return pyperclip.paste()

    def paste_from_clipboard(self):
        self.logger.info('Pasting from clipboard')
        self.keyboard_manager.paste()
