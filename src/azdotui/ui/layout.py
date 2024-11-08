# ui/layout.py

import asyncio
import curses.panel

from azdotui.config.logger import logger
from azdotui.ui.panes.builds_pane import BuildsPane
from azdotui.ui.panes.pipelines_pane import PipelinesPane
from azdotui.ui.panes.projects_pane import ProjectsPane
from azdotui.ui.status_bar import StatusBar


class Layout:
    def __init__(self, screen, azdo_client):
        self.screen = screen
        self.azdo_client = azdo_client
        self.running = True

        self.status_bar = StatusBar(self)

        # Use a dictionary to store panes
        self.panes = {
            "projects": ProjectsPane(self),
            "pipelines": PipelinesPane(self),
            "builds": BuildsPane(self)
        }
        self.pane_order = ["projects", "pipelines", "builds"]
        self.active_pane_name = "projects"
        self.active_pane = self.panes[self.active_pane_name]

        self.full_render_needed = True
        self.input_mode = False
        self.input_buffer = ''
        self.input_prompt = ''
        self.confirmation_mode = False
        self.input_action = None

        self.auto_refresh_tasks = []

        # Start auto-refresh tasks for panes that need it
        for pane in self.panes.values():
            if pane.auto_refresh_interval > 0:
                task = asyncio.create_task(self.auto_refresh_pane(pane))
                self.auto_refresh_tasks.append(task)

    def switch_pane(self):
        current_index = self.pane_order.index(self.active_pane_name)
        self.active_pane_name = self.pane_order[(current_index + 1) % len(self.pane_order)]
        self.active_pane = self.panes[self.active_pane_name]
        self.status_bar.set_message(f"Switched to {self.active_pane.title} pane")
        self.full_render_needed = True

    def render(self):
        # Render active pane if it needs rendering
        if self.active_pane.needs_render:
            self.active_pane.render()
            self.active_pane.needs_render = False

        # Render other panes if full render is needed
        if self.full_render_needed:
            for pane_name, pane in self.panes.items():
                if pane != self.active_pane:
                    pane.render()
            self.full_render_needed = False

        # Always render the status bar
        self.status_bar.render()
        curses.panel.update_panels()
        curses.doupdate()

    def set_input_mode(self, prompt, action):
        self.input_mode = True
        self.input_buffer = ''
        self.input_prompt = prompt
        self.input_action = action
        self.confirmation_mode = False
        self.status_bar.set_message(self.input_prompt)

    async def trigger_selected_pipelines(self):
        branch = self.input_buffer.strip()
        pipelines_pane = self.panes['pipelines']
        selected_pipelines = pipelines_pane.selected_pipelines.copy()
        project_id = pipelines_pane.project_id

        if not selected_pipelines:
            self.status_bar.set_message("No pipelines selected.")
            return

        if not branch:
            self.status_bar.set_message("Branch/tag cannot be empty.")
            return

        tasks = [
            self.azdo_client.trigger_pipeline(project_id, pipeline_id, branch)
            for pipeline_id in selected_pipelines
        ]
        try:
            await asyncio.gather(*tasks)
            self.status_bar.set_message(f"Triggered pipelines on '{branch}'.")
            pipelines_pane.selected_pipelines.clear()
            self.full_render_needed = True  # Refresh UI to update selection marks
        except Exception as e:
            self.status_bar.set_message(f"Failed to trigger pipelines: {e}")
            logger.error(f"Error triggering pipelines: {e}", exc_info=True)

    async def cancel_running_and_queued_builds(self):
        builds_pane = self.panes['builds']
        project_id = builds_pane.project_id

        if not project_id:
            self.status_bar.set_message("No project selected.")
            return

        builds_to_cancel = []
        for category in ['running', 'queued']:
            builds = builds_pane.builds_by_category.get(category, [])
            builds_to_cancel.extend(builds)

        if not builds_to_cancel:
            self.status_bar.set_message("No running or queued builds to cancel.")
            return

        tasks = [
            self.azdo_client.cancel_build(project_id, build['id'])
            for build in builds_to_cancel
        ]

        try:
            await asyncio.gather(*tasks)
            self.status_bar.set_message(f"Cancelled {len(builds_to_cancel)} builds.")
            await builds_pane.refresh_data()  # Refresh the builds pane
        except Exception as e:
            self.status_bar.set_message(f"Failed to cancel builds: {e}")
            logger.error(f"Error cancelling builds: {e}", exc_info=True)

    async def auto_refresh_pane(self, pane):
        while self.running:
            try:
                await pane.refresh_data()
                pane.needs_render = True
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto_refresh_pane for {pane.title}: {e}", exc_info=True)
            await asyncio.sleep(pane.auto_refresh_interval)

