# utils/cursed.py

import curses


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Selected item
    curses.init_pair(2, curses.COLOR_GREEN, -1)                  # Success messages
    curses.init_pair(3, curses.COLOR_YELLOW, -1)                 # Active pane title
    curses.init_pair(4, curses.COLOR_RED, -1)                    # Error messages
    # You can define more color pairs as needed

