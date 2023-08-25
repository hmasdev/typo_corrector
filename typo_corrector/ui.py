from enum import Enum
from functools import partial
from logging import Logger, getLogger
from typing import Callable, Optional

import tkinter as tk
from tkinter import Tk, BooleanVar

from .config import Config, Keybind
from .keyboard_manager import KeyboardManager
from .utils import pipeline


class EConfirmation(Enum):
    YES = "yes"
    JUST_COPY = "just_copy"
    CANCEL = "cancel"


class TkinterUserInterface:
    """User interface using Tkinter
    """

    def __init__(
        self,
        window_size: str = "640x640",
        keyboard_manager: KeyboardManager = KeyboardManager(),
        logger: Logger = getLogger(__name__),
    ) -> None:
        self.widget: Optional[Tk] = None
        self.windows_size = window_size
        self.keyboard_manager = keyboard_manager
        self.activated: bool = False
        self.logger = logger

    def start(self):

        if self.activated:
            self.logger.warning(f'{self.__class__.__name__} has already been activated but start has been called')  # noqa
            return

        assert self.widget is not None
        self.activated = True

        self.logger.debug(f'application ID is {id(self.widget)}')
        self.widget.mainloop()

    def end(self):
        if self.widget is None:
            self.logger.warning(f'{self.__class__.__name__} is None but {self.__class__.__name__} has been called')  # noqa
            return
        if not self.activated:
            self.logger.warning(f'{self.__class__.__name__} has already been deactivated but {self.__class__.__name__} has been called')  # noqa
        self.widget.quit()
        self.widget.destroy()
        self.widget = None
        self.activated = False

    def prepare(self):
        if self.widget is not None:
            self.logger.warning(f'{self.__class__.__name__} is not None but {self.__class__.__name__} has been called')  # noqa
            return
        if self.activated:
            self.logger.warning(f'{self.__class__.__name__} has already been activated but {self.__class__.__name__} has been called')  # noqa
            return
        self.widget = Tk()

        self.widget.geometry(self.windows_size)
        self.widget.withdraw()

    def show_confirmation(
        self,
        text_before: str,
        text_after: str,
        callback: Callable[[EConfirmation], None],
    ):
        dialog = tk.Toplevel(self.widget)
        dialog.geometry(self.windows_size)
        dialog.title("Confirmation")
        self.keyboard_manager.switch_active_window(reverse=True)

        # frames
        frame_before = tk.Frame(dialog)
        frame_after = tk.Frame(dialog)
        frame_buttons = tk.Frame(dialog)

        # components
        label_before = tk.Label(frame_before, text='BEFORE:', anchor="w")
        text_label_before = tk.Label(frame_before, text=text_before, anchor="w")  # noqa
        label_after = tk.Label(frame_after, text='AFTER :', anchor="w")
        text_label_after = tk.Label(frame_after, text=text_after, anchor="w")  # noqa
        yes_btn = tk.Button(
            frame_buttons,
            text="Yes",
            command=pipeline(
                partial(self.logger.debug, "Yes button has been clicked"),
                dialog.destroy,
                partial(callback, EConfirmation.YES),
            )
        )
        copy_btn = tk.Button(
            frame_buttons,
            text="Just copy it into the clipboard",
            command=pipeline(
                partial(self.logger.debug, "Just copy button has been clicked"),  # noqa
                dialog.destroy,
                partial(callback, EConfirmation.JUST_COPY),
            )
        )
        cancel_btn = tk.Button(
            frame_buttons,
            text="Cancel",
            command=pipeline(
                partial(self.logger.debug, "Cancel button has been clicked"),
                dialog.destroy,
                partial(callback, EConfirmation.CANCEL),
            )
        )
        # keybind
        dialog.bind("<Control-Return>", lambda event: yes_btn.invoke())
        dialog.bind("<Shift-Return>", lambda event: copy_btn.invoke())
        dialog.bind("<Escape>", lambda event: cancel_btn.invoke())

        # pack
        frame_before.pack(expand=True, fill=tk.BOTH)
        frame_after.pack(expand=True, fill=tk.BOTH)
        frame_buttons.pack(expand=True, fill=tk.BOTH)

        # align
        label_before.grid(row=0, column=0, sticky=tk.NSEW, columnspan=3, padx=5, pady=5)  # noqa
        text_label_before.grid(row=0, column=3, sticky=tk.NSEW, columnspan=7, padx=5, pady=5)  # noqa
        label_after.grid(row=0, column=0, sticky=tk.NSEW, columnspan=3, padx=5, pady=5)  # noqa
        text_label_after.grid(row=0, column=3, sticky=tk.NSEW, columnspan=7, padx=5, pady=5)  # noqa
        yes_btn.grid(row=0, column=0, sticky=tk.NSEW, columnspan=3, padx=5, pady=5)  # noqa
        copy_btn.grid(row=0, column=4, sticky=tk.NSEW, columnspan=4, padx=5, pady=5)  # noqa
        cancel_btn.grid(row=0, column=8, sticky=tk.NSEW, columnspan=3, padx=5, pady=5)  # noqa

        frame_before.grid_rowconfigure(0, weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[1])//3)  # noqa
        frame_before.grid_columnconfigure(list(range(10)), weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[0])//10)    # type: ignore  # noqa
        frame_after.grid_rowconfigure(0, weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[1])//3)  # noqa
        frame_after.grid_columnconfigure(list(range(10)), weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[0])//10)    # type: ignore  # noqa
        frame_buttons.grid_rowconfigure(0, weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[1])//3)  # noqa
        frame_buttons.grid_columnconfigure(list(range(10)), weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[0])//10)    # type: ignore  # noqa

        self.widget.wait_window(dialog)  # type: ignore

    def show_config(
        self,
        current_config: Config,
        callback: Callable[[Config], None],
    ):

        dialog = tk.Toplevel(self.widget)
        dialog.geometry(self.windows_size)
        dialog.title("config")
        self.keyboard_manager.switch_active_window(reverse=True)

        # show the current config
        # current keybinds
        frame_act_kb_label = tk.Frame(dialog)
        frame_act_kb_userinput = tk.Frame(dialog)
        activation_keybind_label = tk.Label(frame_act_kb_label, text="Activation keybind", anchor="w")    # noqa
        activation_keybind_use_ctrl_var = BooleanVar(value=current_config.activation_keybind.use_ctrl)  # noqa
        activation_keybind_use_alt_var = BooleanVar(value=current_config.activation_keybind.use_alt)  # noqa
        activation_keybind_use_shift_var = BooleanVar(value=current_config.activation_keybind.use_shift)  # noqa
        activation_keybind_use_super_var = BooleanVar(value=current_config.activation_keybind.use_super)  # noqa
        activation_keybind_use_ctrl = tk.Checkbutton(frame_act_kb_userinput, text='ctrl', variable=activation_keybind_use_ctrl_var)  # noqa
        activation_keybind_use_alt = tk.Checkbutton(frame_act_kb_userinput, text='alt', variable=activation_keybind_use_alt_var)  # noqa
        activation_keybind_use_shift = tk.Checkbutton(frame_act_kb_userinput, text='shift', variable=activation_keybind_use_shift_var)  # noqa
        activation_keybind_use_super = tk.Checkbutton(frame_act_kb_userinput, text='super', variable=activation_keybind_use_super_var)  # noqa
        activation_keybind_char = tk.Entry(frame_act_kb_userinput, width=10)
        activation_keybind_char.insert(0, current_config.activation_keybind.char)  # noqa

        frame_conf_kb_label = tk.Frame(dialog)
        frame_conf_kb_userinput = tk.Frame(dialog)
        config_keybind_label = tk.Label(frame_conf_kb_label, text="Config keybind", anchor="w")  # noqa
        config_keybind_use_ctrl_var = BooleanVar(value=current_config.config_keybind.use_ctrl)  # noqa
        config_keybind_use_alt_var = BooleanVar(value=current_config.config_keybind.use_alt)  # noqa
        config_keybind_use_shift_var = BooleanVar(value=current_config.config_keybind.use_shift)  # noqa
        config_keybind_use_super_var = BooleanVar(value=current_config.config_keybind.use_super)  # noqa
        config_keybind_use_ctrl = tk.Checkbutton(frame_conf_kb_userinput, text='ctrl', variable=config_keybind_use_ctrl_var)  # noqa
        config_keybind_use_alt = tk.Checkbutton(frame_conf_kb_userinput, text='alt', variable=config_keybind_use_alt_var)  # noqa
        config_keybind_use_shift = tk.Checkbutton(frame_conf_kb_userinput, text='shift', variable=config_keybind_use_shift_var)  # noqa
        config_keybind_use_super = tk.Checkbutton(frame_conf_kb_userinput, text='super', variable=config_keybind_use_super_var)  # noqa
        config_keybind_char = tk.Entry(frame_conf_kb_userinput, width=10)
        config_keybind_char.insert(0, current_config.config_keybind.char)

        # current assumptions
        frame_condition_label = tk.Frame(dialog)
        frame_condition_userinput = tk.Frame(dialog)
        condition_label = tk.Label(frame_condition_label, text="Condition Text", anchor="w")  # noqa
        condition_str = tk.Text(
            frame_condition_userinput,
            height=int(self.windows_size.split('+')[0].split('x')[1])//100,
            width=int(self.windows_size.split('+')[0].split('x')[0]),
        )
        condition_str.insert(tk.END, current_config.condition_str)

        frame_example_label = tk.Frame(dialog)
        frame_example_userinput = tk.Frame(dialog)
        example_label = tk.Label(
            frame_example_label, text="Example Text", anchor="w")
        example_str = tk.Text(
            frame_example_userinput,
            height=int(self.windows_size.split('+')[0].split('x')[1])//100,
            width=int(self.windows_size.split('+')[0].split('x')[0]),
        )
        example_str.insert(tk.END, current_config.example_str)

        # buttons
        frame_buttons = tk.Frame(dialog)
        ok_button = tk.Button(
            frame_buttons,
            text="OK",
            command=pipeline(
                partial(self.logger.debug, "OK button has been clicked"),
                lambda *args, **kwargs: Config(
                    activation_keybind=Keybind(
                        use_ctrl=activation_keybind_use_ctrl_var.get(),
                        use_alt=activation_keybind_use_alt_var.get(),
                        use_shift=activation_keybind_use_shift_var.get(),
                        use_super=activation_keybind_use_super_var.get(),
                        char=activation_keybind_char.get(),
                    ),
                    config_keybind=Keybind(
                        use_ctrl=config_keybind_use_ctrl_var.get(),
                        use_alt=config_keybind_use_alt_var.get(),
                        use_shift=config_keybind_use_shift_var.get(),
                        use_super=config_keybind_use_super_var.get(),
                        char=config_keybind_char.get(),
                    ),
                    condition_str=condition_str.get("1.0", tk.END),
                    example_str=example_str.get("1.0", tk.END),
                ),
                lambda *args, **kwargs: dialog.destroy(),
                callback,
            )
        )
        cancel_btn = tk.Button(
            frame_buttons,
            text="Cancel",
            command=pipeline(
                partial(self.logger.debug, "Cancel button has been clicked"),
                dialog.destroy,
                partial(callback, current_config),
            )
        )
        # keybind
        dialog.bind("<Control-Return>", lambda event: ok_button.invoke())
        dialog.bind("<Escape>", lambda event: cancel_btn.invoke())

        # pack
        frame_act_kb_label.pack(expand=True, fill=tk.BOTH)
        frame_act_kb_userinput.pack(expand=True, fill=tk.BOTH)
        frame_conf_kb_label.pack(expand=True, fill=tk.BOTH)
        frame_conf_kb_userinput.pack(expand=True, fill=tk.BOTH)
        frame_condition_label.pack(expand=True, fill=tk.BOTH)
        frame_condition_userinput.pack(expand=True, fill=tk.BOTH)
        frame_example_label.pack(expand=True, fill=tk.BOTH)
        frame_example_userinput.pack(expand=True, fill=tk.BOTH)
        frame_buttons.pack(expand=True, fill=tk.BOTH)

        # align
        activation_keybind_label.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        activation_keybind_use_ctrl.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        activation_keybind_use_alt.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        activation_keybind_use_shift.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        activation_keybind_use_super.grid(row=0, column=3, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        activation_keybind_char.grid(row=0, column=4, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_label.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_use_ctrl.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_use_alt.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_use_shift.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_use_super.grid(row=0, column=3, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        config_keybind_char.grid(row=0, column=4, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        condition_label.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        condition_str.grid(row=0, column=0, columnspan=5, rowspan=3, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        example_label.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        example_str.grid(row=0, column=0, columnspan=5, rowspan=3, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        ok_button.grid(row=0, column=1, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)  # noqa
        cancel_btn.grid(row=0, column=3, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)  # noqa

        for _frame in [
            frame_act_kb_label,
            frame_act_kb_userinput,
            frame_conf_kb_label,
            frame_conf_kb_userinput,
            frame_condition_label,
            frame_condition_userinput,
            frame_example_label,
            frame_example_userinput,
        ]:
            _frame.grid_rowconfigure(0, weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[1])//13)  # noqa
            _frame.grid_columnconfigure(list(range(5)), weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[0])//5)  # type: ignore  # noqa
        frame_buttons.grid_columnconfigure(list(range(5)), weight=1, minsize=int(self.windows_size.split('+')[0].split('x')[0])//5)  # type: ignore  # noqa

        self.widget.wait_window(dialog)  # type: ignore
