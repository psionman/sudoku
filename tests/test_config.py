from pathlib import Path

from sudoku.config import read_config


def test_config_no_directory(mocker):
    # pylint: disable=no-member)
    mocker.patch(
        'sudoku.config.CONFIG_PATH',
        Path(
            Path(__file__).parent,
            'test_data',
            'not a directory',
            'config.toml')
        )

    config = read_config()
    assert config.default_blocks == 1


def test_config_save(mocker):
    # pylint: disable=no-member)
    mocker.patch(
        'sudoku.config.CONFIG_PATH',
        Path(Path(__file__).parent, 'test_data', 'config', 'config.toml')
        )

    config = read_config()
    if config.path.is_file():
        config.path.unlink()

    config = read_config()
    # config.update('default_blocks', 6)
    # config.save()

    # config = read_config()

    # assert config.default_blocks == 6
