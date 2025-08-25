"""Constants for Sudoku."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir

from psiutils.known_paths import resolve_path

# General
AUTHOR = 'Jeff Watkins'
APP_NAME = 'sudoku'
APP_AUTHOR = 'psionman'
HTML_DIR = resolve_path('html', __file__)
HELP_URI = ''

# Paths
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), 'config.toml')
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
USER_DATA_FILE = 'data.json'
HOME = str(Path.home())

# GUI
APP_TITLE = 'Sudoku'
ICON_FILE = Path(Path(__file__).parent, 'images', 'icon.png')

DEFAULT_BLOCKS: int = 1
