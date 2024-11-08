# ui/panes/base_pane.py

import curses


class BasePane:
    def __init__(self, layout, width_ratio, x_start):
        self.layout = layout
        self.width_ratio = width_ratio
        self.x_start = x_start
        self.window = None
        self.panel = None
        self.is_loading = False
        self.needs_render = True
        self.initialize_window()

        # Common attributes
        self.items = []
        self.selected_index = 0
        self.viewport_start = 0
        self.title = ''
        self.auto_refresh_interval = 0  # Default to no auto-refresh

    def initialize_window(self):
        max_y, max_x = self.layout.screen.getmaxyx()
        width = int(max_x * self.width_ratio)
        x = int(max_x * self.x_start)
        self.window = curses.newwin(max_y - 1, width, 0, x)
        self.panel = curses.panel.new_panel(self.window)

    def render(self):
        pass  # To be implemented by subclasses


    def navigate(self, direction):
        if direction == 'UP':
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.viewport_start:
                    self.viewport_start -= 1
                self.needs_render = True
        elif direction == 'DOWN':
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
                max_y = self.window.getmaxyx()[0] - 2  # Minus borders
                if self.selected_index >= self.viewport_start + max_y:
                    self.viewport_start += 1
                self.needs_render = True

    async def handle_input(self, key):
        pass  # To be implemented by subclasses

    async def handle_selection(self):
        pass  # To be implemented by subclasses

    async def refresh_data(self):
        pass  # To be implemented by subclasses

