from sudoku.grid import Grid
from sudoku.config import read_config

config = read_config()


def test_defaults() -> None:
    # pylint: disable=no-member)
    grid = Grid()
    assert grid.blocks == config.default_blocks
