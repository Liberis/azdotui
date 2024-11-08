# ui/panes/builds_pane.py

import asyncio
import curses
import logging
from collections import defaultdict

from dateutil import parser  # Import dateutil.parser

from .base_pane import BasePane

logger = logging.getLogger(__name__)

class BuildsPane(BasePane):
    def __init__(self, layout):
        super().__init__(layout, width_ratio=1/3, x_start=2/3)
        self.title = 'Builds'
        self.build_status = {}
        self.auto_refresh_interval = 5  # Fetch every 5 seconds
        self.project_id = None
        self.pipeline_id = None
        self.builds_by_category = defaultdict(list)

    async def load_builds(self, project_id):
        self.project_id = project_id
        self.pipeline_id = None  # Reset pipeline filter
        await self.refresh_data()

    async def load_builds_for_pipeline(self, project_id, pipeline_id):
        self.project_id = project_id
        self.pipeline_id = pipeline_id
        await self.refresh_data()

    async def refresh_data(self):
        self.is_loading = True
        self.needs_render = True
        try:
            if self.project_id:
                if self.pipeline_id:
                    # Fetch builds for specific pipeline
                    data = await self.layout.azdo_client.get_build_status(self.project_id, self.pipeline_id)
                else:
                    # Fetch builds for the project
                    data = await self.layout.azdo_client.get_all_builds(self.project_id)
                builds = data.get('value', [])
                # Categorize builds
                self.builds_by_category = self.categorize_builds(builds)
                self.items = builds  # For navigation purposes
                self.selected_index = 0
                self.viewport_start = 0
                self.layout.full_render_needed = True
        except asyncio.CancelledError:
            raise  # Re-raise to allow task cancellation
        except Exception as e:
            logger.error(f"Error loading builds: {e}", exc_info=True)
            # Ensure builds_by_category is set to an empty defaultdict
            self.builds_by_category = defaultdict(list)
            self.items = []
        finally:
            self.is_loading = False
            self.needs_render = True  # Ensure the pane is re-rendered

    def categorize_builds(self, builds):
        categories = {
            'succeeded': [],
            'failed': [],
            'warning': [],
            'queued': [],
            'running': []
        }
        for build in builds:
            status = build.get('status', '').lower()
            result = build.get('result', '').lower()
            if status == 'completed':
                if result == 'succeeded':
                    categories['succeeded'].append(build)
                elif result == 'failed':
                    categories['failed'].append(build)
                elif result == 'partiallysucceeded':
                    categories['warning'].append(build)
                else:
                    categories['warning'].append(build)
            elif status == 'inprogress':
                categories['running'].append(build)
            elif status == 'notstarted':
                categories['queued'].append(build)
            else:
                # You can add other status handling if needed
                pass
        return categories

    def render(self):
        if not self.needs_render:
            return
        self.window.erase()
        self.window.border()
        self.window.addstr(0, 2, f' {self.title} ', curses.A_BOLD)
        max_y, max_x = self.window.getmaxyx()
        visible_height = max_y - 2  # Minus borders

        if self.is_loading:
            self.window.addstr(1, 2, "Loading...", curses.A_DIM)
        else:
            y = 1
            categories_order = ['succeeded', 'failed', 'warning', 'queued', 'running']
            for category in categories_order:
                builds = self.builds_by_category.get(category, [])
                if builds:
                    # Display category as a header
                    self.window.addnstr(y, 2, f"== {category.capitalize()} ==", max_x - 4, curses.A_BOLD)
                    y += 1
                    count = 0
                    for build in builds:
                        if y >= max_y - 1 or count >= 5:
                            break  # Prevent drawing outside the window or exceeding 5 builds per category
                        display_text = self.format_item(build)
                        self.window.addnstr(y, 2, display_text, max_x - 4)
                        y += 1
                        count +=1
                if y >= max_y - 1:
                    break
        self.panel.top()
        self.panel.show()
        self.needs_render = False

    def format_item(self, item):
        pipeline_name = item.get('definition', {}).get('name', 'Unknown Pipeline')
        build_number = item.get('buildNumber', 'N/A')
        result_text = item.get('result', 'N/A')
        queue_time = item.get('queueTime', '')
        queue_time_formatted = ''
        if queue_time:
            try:
                dt = parser.isoparse(queue_time)
                queue_time_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                logger.error(f"Error parsing queue_time '{queue_time}': {e}")
                queue_time_formatted = queue_time  # Fallback to original string
        return f"{pipeline_name} #{build_number}: {result_text} at {queue_time_formatted}"

    def navigate(self, direction):
        # Navigation logic can be implemented if needed
        pass

    async def handle_selection(self):
        # Handle selection if needed
        pass

    async def handle_input(self, key):
        if key == ord('c'):
            # 'c' key pressed, start input mode to cancel builds
            self.layout.start_input_mode(prompt="Cancel all running and queued builds? (y/n): ")
            self.layout.input_action = 'cancel_builds'
        else:
            pass  # Other keys can be handled here

