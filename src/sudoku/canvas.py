"""Handle the canvas class for sudoku."""

import tkinter as tk

from sudoku.grid import Frame

COLOURS = [
    ("#AEC6CF", "#5B9BD5"),  # blue
    ("#FFB347", "#F58220"),  # orange
    ("#B39EB5", "#8E44AD"),  # purple
    ("#77DD77", "#27AE60"),  # green
    ("#FF6961", "#E74C3C"),  # red
    ("#FDFD96", "#F1C40F"),  # yellow
]


class Canvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = '#fff'
        self.selected = '#000'
        self.id = str(self).replace('.', 'A').replace('!', 'B')
        self._colours = (self.background, self.selected)
        self.frame: Frame = None
        self.inner: tk.Canvas = None
        self.suggestion: int = 0
        self.solution: int = 0

    @property
    def colours(self):
        return self._colours

    @colours.setter
    def colours(self, value: tuple) -> None:
        self.background = value[0]
        self.selected = value[1]
        self._colours = (self.background, self.selected)
