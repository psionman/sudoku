"""ConfigFrame for Sudoku."""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD, Pad
from psiutils.utilities import window_resize, logger

from sudoku.constants import APP_TITLE
from sudoku.config import read_config
import sudoku.text as txt

FIELDS = {
    "data_directory": tk.StringVar,
    "my_int": tk.IntVar,
    "my_bool": tk.BooleanVar,
}


class ConfigFrame():
    """
    A configuration dialog for editing application settings.
    """

    data_directory: tk.StringVar
    my_int: tk.IntVar
    my_bool: tk.BooleanVar

    def __init__(self, parent: tk.Frame) -> None:
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        config = read_config()
        self.config = config


        # tk variables

        for field, f_type in FIELDS.items():
            if f_type is tk.StringVar:
                setattr(self, field, self._stringvar(getattr(config, field)))
            elif f_type is tk.IntVar:
                setattr(self, field, self._intvar(getattr(config, field)))
            elif f_type is tk.BooleanVar:
                setattr(self, field, self._boolvar(getattr(config, field)))

        self._show()

    def _stringvar(self, value: str) -> tk.StringVar:
        stringvar = tk.StringVar(value=value)
        stringvar.trace_add('write', self._check_value_changed)
        return stringvar

    def _intvar(self, value: int) -> tk.IntVar:
        intvar = tk.IntVar(value=value)
        intvar.trace_add('write', self._check_value_changed)
        return intvar

    def _boolvar(self, value: bool) -> tk.BooleanVar:
        boolvar = tk.BooleanVar(value=value)
        boolvar.trace_add('write', self._check_value_changed)
        return boolvar

    def _show(self) -> None:
        """
        Initialize and display the configuration form GUI.
        """
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(f'{APP_TITLE} - {txt.CONFIG}')

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-s>', self._save_config)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        """
        Create and return the main frame containing form input widgets.
        """
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text='label text')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, 'open', False, self._get_data_directory)
        button.grid(row=row, column=2, padx=Pad.W)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        """
        Create and return the button frame for the form.
        """
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', True, self._save_config),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _check_value_changed(self, *args) -> bool:
        """
        Enable or disable form buttons based on changes in configuration.
        """
        enable = bool(self._config_changes())
        self.button_frame.enable(enable)

    def _get_data_directory(self, *args) -> None:
        """
        Prompt the user to select a new data directory and update the value.
        """
        data_directory = filedialog.askdirectory(
            initialdir=Path(self.data_directory.get()),
            parent=self.root,
        )
        if data_directory:
            self.data_directory.set(data_directory)

    def _save_config(self):
        changes = {field: f'(old value={change[0]}, new_value={change[1]})'
                   for field, change in self._config_changes().items()}

        logger.info(
            "Config saved",
            changes=changes
        )

        for field in FIELDS:
            self.config.config[field] = getattr(self, field).get()
        return self.config.save()

    def _config_changes(self) -> dict:
        stored = self.config.config
        return {
            field: (stored[field], getattr(self, field).get())
            for field in FIELDS
            if stored[field] != getattr(self, field).get()
        }

    def _dismiss(self, *args) -> None:
        """
        Close the configuration window and terminate the application.
        """
        self.root.destroy()
