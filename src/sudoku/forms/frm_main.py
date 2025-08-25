
"""MainFrame for Sudoku."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import random

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame
from psiutils.utilities import window_resize

from sudoku.constants import APP_TITLE
from sudoku.config import read_config

from sudoku.main_menu import MainMenu
# from sudoku.forms.frmModal import ModalFrame

from sudoku.grid import Grid, Block, Frame
from sudoku.canvas import Canvas, COLOURS

FRAME_TITLE = APP_TITLE


TOTAL_LEFT, TOTAL_TOP = 3, 3
TOTAL_WIDTH, TOTAL_HEIGHT = 50, 50
TOTAL_TEXT_LEFT, TOTAL_TEXT_TOP = 25, 25
TOTAL_FONT = ("Arial", 24)

SUGGESTION_LEFT, SUGGESTION_TOP = 60, 60
SUGGESTION_WIDTH, SUGGESTION_HEIGHT = 50, 50
SUGGESTION_TEXT_LEFT, SUGGESTION_TEXT_TOP = 25, 25
SUGGESTION_FONT = ("Arial", 36)


class MainFrame():
    """Create MainFrame for Sudoku application."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = read_config()
        self.canvases = {}
        self.r2l_index, self.l2r_index = 0, 0
        self.left_to_right = True
        self.buttons = {}

        # tk variables

        # Trace

        self._show()
        self._create_grid()
        self.root.update_idletasks()  # Refresh UI without full redraw
        self.root.resizable(False, False)

    def _show(self):
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-n>', self._create_grid)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        self.root.after(100, self._create_grid)

        self.main_frame = self._main_frame(root)
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # self.main_frame.bind("<Configure>", self._create_grid)

        numeric_frame = self._numeric_frame(root)
        numeric_frame.grid(row=1, column=0)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=2, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        root.bind("<Configure>", self._create_root)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        return frame

    def _numeric_frame(self, master: tk.Frame):
        frame = ttk.Frame(master)
        for number in range(9):
            button = ttk.Button(frame, text=number+1)
            row, column = number // 3, number % 3
            button.grid(row=row, column=column, ipady=20, padx=2, pady=2)
            self.buttons[number] = button
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('new', False, self._create_grid),
            frame.icon_button('close', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _create_grid(self, *args) -> None:
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.grid = Grid()

        # Start test
        # test = 1
        # test_blocks = {
        #     0: Block(
        #         (Frame([1, 4]),
        #          Frame([2, 8]),
        #          Frame([3, 9]),
        #          Frame([5, 7]),
        #          Frame([6])),
        #         ),
        #     1: Block(
        #         (Frame([2, 3, 5, 9]),
        #          Frame([1, 6, 7]),
        #          Frame([8]),
        #          Frame([4])),
        #         )
        #         }
        # if test:
        #     self.grid.blocks = (test_blocks[0],)
        # End test

        self._enable_buttons()
        self.left_to_right = True
        self.r2l_index, self.l2r_index = 0, 0
        for index, block in enumerate(self.grid.blocks):
            block_frame = self._block_frame(block)

            row, column = index // 3, index % 3
            block_frame.grid(row=row, column=column,
                             sticky=tk.NSEW, padx=PAD, pady=PAD)

    def _block_frame(self, block: Block) -> ttk.Frame:
        tk_frame = ttk.Frame(self.main_frame)
        for item in range(3):
            tk_frame.rowconfigure(item, weight=1, uniform="cell")
            tk_frame.columnconfigure(item, weight=1, uniform="cell")

        available_colours = list(COLOURS)

        size = min(self.main_frame.winfo_width(),
                   self.main_frame.winfo_height()) // 3

        self.canvases = self._create_canvases(tk_frame, size)
        canvases = dict(enumerate(self.canvases.values()))

        index = 0
        for frame in block.frames:
            colours = random.choice(available_colours)
            available_colours.remove(colours)

            for cell_index in range(len(frame.cells)):
                canvas = self._setup_cell_canvas(
                    canvases[index], frame, colours)

                if cell_index == 0:
                    self._create_total_text(canvas, frame.total)

                if frame.suggestions[cell_index]:
                    suggestion = frame.suggestions[cell_index]
                    self._create_suggestion_canvas(canvas, suggestion)
                    self.buttons[suggestion - 1].state(["disabled"])

                index = self._get_next_cell_position(frame, cell_index)
        return tk_frame

    def _setup_cell_canvas(
            self,
            canvas: tk.Canvas,
            frame: Frame,
            colours: tuple) -> tk.Canvas:
        canvas.value = frame
        canvas.colours = colours
        canvas['bg'] = canvas.background
        return canvas

    def _create_total_text(self, canvas: tk.Canvas, total: int):
        inner = tk.Canvas(
            canvas, width=TOTAL_WIDTH, height=TOTAL_HEIGHT,
            bg=canvas.selected, borderwidth=0,
            highlightthickness=0)
        canvas.create_window(
            TOTAL_LEFT, TOTAL_TOP, window=inner, anchor=tk.NW)
        canvas.inner = inner.create_text(
            TOTAL_TEXT_LEFT, TOTAL_TEXT_TOP, text=total,
            font=TOTAL_FONT, fill="black")

    def _create_suggestion_canvas(self, canvas: tk.Canvas, suggestion: int):
        inner = tk.Canvas(
            canvas,
            width=SUGGESTION_WIDTH, height=SUGGESTION_HEIGHT,
            bg=canvas.background, borderwidth=0,
            highlightthickness=0)
        canvas.create_window(
            SUGGESTION_LEFT, SUGGESTION_TOP,
            window=inner, anchor=tk.NW)
        canvas.inner = inner.create_text(
            SUGGESTION_TEXT_LEFT, SUGGESTION_TEXT_TOP,
            text=suggestion,
            font=SUGGESTION_FONT, fill="black")

    def _get_next_cell_position(self, frame: Frame, cell_index: int) -> int:
        """Return the index of the next cell to be allocated."""
        cells = len(frame.cells)

        if self.left_to_right:
            # End of row → switch direction
            if (self.l2r_index in (2, 5)
                    and cells > 1 and cell_index >= cells - 2):
                self.r2l_index = self.l2r_index + 3
                self.left_to_right = False
                return self.r2l_index

            self.l2r_index += 1
            return self.l2r_index

        # Right-to-left movement
        self.l2r_index += 1
        self.r2l_index -= 1

        if self.r2l_index in (2, 5):
            self.left_to_right = True
            self.l2r_index += 1
            return self.l2r_index

        return self.r2l_index

    def _create_canvases(self, frame: tk.Frame, size: int) -> dict:
        canvases = {}
        for index in range(9):
            # pylint: disable=no-member)
            cell_canvas = self._create_cell(frame, size)
            row, column = index // 3, index % 3
            cell_canvas.grid(
                row=row,
                column=column,
                padx=0,
                pady=0,
                ipadx=0,
                ipady=0,
                sticky="nsew")
            canvases[cell_canvas.id] = cell_canvas
        return canvases

    def _create_cell(self, frame: tk.Frame, size: int) -> Canvas:
        cell = Canvas(
            frame,
            borderwidth=1,
            background='#fff',
            highlightthickness=2,
            width=size,
            height=size
        )
        cell.bind('<Button-1>', self._cell_selected)

        # Force the canvas to remain square
        def resize(event, canvas=cell):
            side = min(event.width, event.height)
            canvas.config(width=side, height=side)

        cell.bind("<Configure>", resize)
        return cell

    def _cell_selected(self, event) -> None:
        for canvas in self.canvases.values():
            canvas['bg'] = canvas.background
        canvas = self.canvases[event.widget.id]
        canvas['bg'] = canvas.selected

    def _create_root(self, *args) -> None:
        self.main_frame.height = self.main_frame.winfo_width()

    def _enable_buttons(self) -> None:
        for index in range(9):
            self.buttons[index].state(['!disabled'])

    def _disable_buttons(self, all: bool = False) -> None:
        for index in range(9):
            self.buttons[index].state(['!disabled'])

    def _dismiss(self, *args) -> None:
        self.root.destroy()
