# ui/status_bar.py

import curses


class StatusBar:
    def __init__(self, layout):
        self.layout = layout
        self.window = layout.screen.subwin(1, curses.COLS, curses.LINES - 1, 0)
        self.message = ''
        self.needs_render = True

    def set_message(self, message):
        self.message = message
        self.needs_render = True

    def render(self):
        if self.needs_render:
            self.window.erase()
            self.window.addstr(0, 0, self.message[:curses.COLS - 1])
            self.window.refresh()
            self.needs_render = False

