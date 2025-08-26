"""Generate and control a sudoku grid."""
import random
import itertools
from itertools import combinations
import uuid

from psiutils.utilities import logger
from sudoku.config import read_config

FRAMES = {
    2: [(4, 5), (6, 3)],
    3: [(3, 3, 3), (4, 3, 2), (4, 4, 1)],
    4: [(3, 2, 2, 2), (3, 3, 2, 1), (4, 2, 2, 1)],
    5: [(2, 2, 2, 2, 1)],
}
SEPARATOR = '-'*50


class Frame:
    """A sudoku frame."""
    def __init__(self, cells: tuple) -> None:
        self._cells: list = cells
        self.suggestions: dict = {}
        self.uuid = uuid.uuid1()

    def __repr__(self) -> str:
        return (f"Frame({self.total} "
                f"{[str(cell) for cell in self.cells]} "
                f"suggestions {self.suggestions})")

    @property
    def cells(self) -> tuple:
        """Return a sorted tuple of cells."""
        return tuple(sorted(self._cells))

    @property
    def total(self) -> int:
        """Return to sum of the cells in the frame."""
        return sum(self.cells)


class Block:
    """A sudoku block."""
    def __init__(self, frames: tuple = ()) -> None:
        self.frames = frames

    def __repr__(self) -> str:
        return f"Block({[str(frame) for frame in self.frames]})"


class Grid:
    """A sudoku grid."""
    def __init__(self, block_qty: int = 0) -> None:
        # pylint: disable=no-member)
        config = read_config()
        if not block_qty:
            block_qty = config.default_blocks
        self.block_qty = block_qty
        self.blocks = self._create()

        logger.info(f"Grid created {str(self.blocks)}")

    def _create(self) -> None:
        blocks = []
        for _ in range(self.block_qty):
            block = self._get_block()
            self._build_block(block)
            blocks.append(block)
            logger.info(f"Block created {block}")
        return tuple(blocks)

    def _get_block(self) -> tuple:
        elements = random.choice([2, 3, 4, 5])
        frame_set = random.choice(FRAMES[elements])
        numbers = list(range(1, 10))
        frames = []
        for cells in frame_set:
            frame = []
            for _ in range(cells):
                number = random.choice(numbers)
                frame.append(number)
                numbers.remove(number)
            frames.append(Frame(tuple(frame)))
        block = Block(tuple(frames))
        return block

    def _build_block(self, block: Block):
        numbers = list(range(1, 10))
        for frame in block.frames:
            frame.suggestions = self._get_suggestion(frame, numbers)
            for cell in frame.cells:
                if cell in numbers:
                    numbers.remove(cell)
            logger.info(f"Frame built {frame}")

    def _get_suggestion(self, frame: Frame, numbers: list[int]) -> dict:
        """Assign the suggestions to a cell."""
        suggestions = self._generate_suggestion(frame, numbers)

        assigned = {index: 0 for index, cell in enumerate(frame.cells)}
        for suggestion in suggestions:
            cell = random.randint(0, len(frame.cells) - 1)
            while assigned[cell] > 0:
                cell = random.randint(0, len(frame.cells) - 1)
            assigned[cell] = suggestion
        return assigned

    def _generate_suggestion(
            self, frame: Frame, numbers: list[int]) -> list[int]:
        # if there is only one possible outcome return an empty list
        possibles = self._possible_cells(
            frame.total, len(frame.cells), [], numbers)
        if len(possibles) == 1:
            return []

        # otherwise return a list of integers as suggestions
        frame_suggestion = []
        suggestions = self._frame_suggestions(frame)  # a list of suggestions
        for suggestion in suggestions:  # each suggestion is a list of ints
            for number in suggestion:
                numbers.remove(number)
            possibles = self._possible_cells(
                frame.total, len(frame.cells), suggestion, numbers)
            if len(possibles) == 1:
                frame_suggestion = suggestion
                break
            numbers = numbers + suggestion

        return frame_suggestion

    def _possible_cells(
            self, total: int,
            cells: int,
            suggestions: list,
            numbers: list[int]
            ) -> tuple:
        """Return the possible combinations to make the frame."""
        possibles = []
        for possible in combinations(numbers, cells-len(suggestions)):
            possible = [_ for _ in possible] + suggestions
            if (sum(possible) == total
                    and all(v in possible for v in suggestions)):
                possibles.append(possible)
        return tuple(possibles)

    def _frame_suggestions(self, frame: Frame) -> list[list[int]]:
        suggestions = []
        for range_ in range(1, len(frame.cells) + 1):
            for combination in itertools.combinations(
                    frame.cells, range_):
                suggestions.append(list(combination))
        return suggestions
