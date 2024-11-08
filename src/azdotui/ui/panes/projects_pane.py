# ui/panes/projects_pane.py

import curses
import logging

from .base_pane import BasePane

logger = logging.getLogger(__name__)

class ProjectsPane(BasePane):
    def __init__(self, layout):
        super().__init__(layout, width_ratio=1/3, x_start=0)
        self.title = 'Projects'
        self.projects = []
        self.items = []
        self.selected_index = 0
        self.viewport_start = 0
        self.is_loading = False
        self.needs_render = True

    async def refresh_data(self):
        self.is_loading = True
        self.needs_render = True
        try:
            data = await self.layout.azdo_client.get_projects()
            self.projects = data.get('value', [])
            self.items = self.projects
            self.selected_index = 0
            self.viewport_start = 0
            self.layout.full_render_needed = True
        except Exception as e:
            logger.error(f"Error loading projects: {e}", exc_info=True)
            self.items = []
            self.projects = []
        finally:
            self.is_loading = False
            self.needs_render = True

    def render(self):
        self.window.erase()
        self.window.border()

        # Highlight the pane title if it's the active pane
        if self.layout.active_pane == self:
            title_style = curses.A_BOLD | curses.A_REVERSE
        else:
            title_style = curses.A_BOLD

        self.window.addstr(0, 2, f' {self.title} ', title_style)
        max_y, max_x = self.window.getmaxyx()

        if self.is_loading:
            self.window.addstr(1, 2, "Loading...", curses.A_DIM)
        else:
            visible_height = max_y - 2  # Minus borders
            for idx, item in enumerate(self.items[self.viewport_start:self.viewport_start + visible_height]):
                y = idx + 1
                if idx + self.viewport_start == self.selected_index:
                    style = curses.A_REVERSE
                else:
                    style = curses.A_NORMAL
                self.window.addnstr(y, 2, self.format_item(item), max_x - 4, style)

        self.panel.top()
        self.panel.show()
        self.window.noutrefresh()

    def format_item(self, item):
        return item['name'][:self.window.getmaxyx()[1] - 4]

    async def handle_selection(self):
        if not self.items:
            return
        project = self.items[self.selected_index]
        project_id = project['id']
        self.layout.status_bar.set_message(f"Selected Project: {project['name']}")
        # Load pipelines for the selected project
        await self.layout.panes['pipelines'].load_pipelines(project_id)
        # Load builds for the selected project
        await self.layout.panes['builds'].load_builds(project_id)

