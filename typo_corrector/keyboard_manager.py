from logging import getLogger, Logger
import pyautogui


class KeyboardManager:

    def __init__(self, logger: Logger = getLogger(__name__)) -> None:
        self.logger = logger

    def switch_active_window(self, reverse: bool = False):
        self.logger.debug('Switching active window (alt+tab or alt+shift+tab)')
        pyautogui.keyDown('alt')
        if reverse:
            pyautogui.keyDown('shift')
        pyautogui.press('tab')
        if reverse:
            pyautogui.keyUp('shift')
        pyautogui.keyUp('alt')

    def copy(self):
        self.logger.debug('Copying (ctrl+c)')
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('c')
        pyautogui.keyUp('c')
        pyautogui.keyUp('ctrl')

    def paste(self):
        self.logger.debug('Pasting (ctrl+v)')
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('v')
        pyautogui.keyUp('v')
        pyautogui.keyUp('ctrl')
