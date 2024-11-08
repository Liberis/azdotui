# ui/panes/pipelines_pane.py

import curses
import logging

from azdotui.utils.tree import build_tree

from .base_pane import BasePane

logger = logging.getLogger(__name__)

class PipelinesPane(BasePane):
    def __init__(self, layout):
        super().__init__(layout, width_ratio=1/3, x_start=1/3)
        self.title = 'Pipelines'
        self.project_id = None
        self.pipelines = []
        self.tree_root = None  # Root of the pipelines tree
        self.items = []
        self.selected_pipelines = set()
        self.is_loading = False
        self.needs_render = True
        self.selected_index = 0
        self.viewport_start = 0

    async def load_pipelines(self, project_id):
        self.project_id = project_id
        await self.refresh_data()

    async def refresh_data(self):
        if not self.project_id:
            return
        self.is_loading = True
        self.needs_render = True
        try:
            data = await self.layout.azdo_client.get_pipelines(self.project_id)
            self.pipelines = data.get('value', [])
            self.tree_root = build_tree(self.pipelines)
            self.items = self.flatten_tree(self.tree_root)
            self.selected_index = 0
            self.viewport_start = 0
            self.layout.full_render_needed = True
        except Exception as e:
            logger.error(f"Error loading pipelines: {e}", exc_info=True)
            self.items = []
            self.pipelines = []
            self.tree_root = None
        finally:
            self.is_loading = False
            self.needs_render = True

    def flatten_tree(self, node, level=0):
        """
        Recursively flatten the tree into a list for rendering.

        Args:
            node (TreeNode): The current node in the tree.
            level (int): The current depth level in the tree for indentation.

        Returns:
            list: A list of TreeNode instances in the order they should be displayed.
        """
        flattened = []
        if node.name != 'root':
            node.level = level
            flattened.append(node)
        if node.is_folder and node.expanded:
            for child in node.children:
                flattened.extend(self.flatten_tree(child, level + 1))
        return flattened

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
            for idx, node in enumerate(self.items[self.viewport_start:self.viewport_start + visible_height]):
                y = idx + 1
                if idx + self.viewport_start == self.selected_index:
                    style = curses.A_REVERSE
                else:
                    style = curses.A_NORMAL

                prefix = ' ' * node.level * 2
                if node.is_folder:
                    # Determine folder selection status
                    all_selected = self.are_all_pipelines_selected(node)
                    checkbox = '[x]' if all_selected else '[ ]'
                    marker = '-' if node.expanded else '+'
                    line = f"{prefix}{marker} {checkbox} {node.name}"
                else:
                    checkbox = '[x]' if node.pipeline_id in self.selected_pipelines else '[ ]'
                    line = f"{prefix}{checkbox} {node.name}"
                self.window.addnstr(y, 2, line, max_x - 4, style)

        self.panel.top()
        self.panel.show()
        self.window.noutrefresh()

    async def handle_input(self, key):
        if not self.items:
            return
        node = self.items[self.selected_index]
        if key == ord(' '):
            if node.is_folder:
                # Toggle selection of all pipelines under this folder
                pipeline_ids = self.get_all_pipeline_ids(node)
                if self.are_all_pipelines_selected(node):
                    self.deselect_pipelines(pipeline_ids)
                else:
                    self.select_pipelines(pipeline_ids)
                self.needs_render = True
            else:
                # Toggle selection of individual pipeline
                if node.pipeline_id in self.selected_pipelines:
                    self.selected_pipelines.remove(node.pipeline_id)
                else:
                    self.selected_pipelines.add(node.pipeline_id)
                self.needs_render = True
        elif key == curses.KEY_LEFT:
            await self.collapse_node(node)
        elif key == curses.KEY_RIGHT:
            await self.expand_node(node)

    async def handle_selection(self):
        node = self.items[self.selected_index]
        if node.is_folder:
            # Toggle expansion
            node.expanded = not node.expanded
            self.items = self.flatten_tree(self.tree_root)
            self.needs_render = True
        else:
            # Load builds for the selected pipeline
            await self.layout.panes['builds'].load_builds_for_pipeline(self.project_id, node.pipeline_id)

    async def collapse_node(self, node):
        if node.is_folder and node.expanded:
            node.expanded = False
            self.items = self.flatten_tree(self.tree_root)
            self.needs_render = True
        else:
            # Move to parent node if possible
            parent_node = self.find_parent_node(self.tree_root, node)
            if parent_node and parent_node != self.tree_root:
                self.selected_index = self.items.index(parent_node)
                self.needs_render = True

    async def expand_node(self, node):
        if node.is_folder and not node.expanded:
            node.expanded = True
            self.items = self.flatten_tree(self.tree_root)
            self.needs_render = True

    def find_parent_node(self, current_node, target_node):
        """
        Recursively find the parent of the target node.

        Args:
            current_node (TreeNode): The node to start searching from.
            target_node (TreeNode): The node whose parent is to be found.

        Returns:
            TreeNode or None: The parent node if found, else None.
        """
        for child in current_node.children:
            if child == target_node:
                return current_node
            if child.is_folder:
                result = self.find_parent_node(child, target_node)
                if result:
                    return result
        return None

    def get_all_pipeline_ids(self, node):
        """
        Recursively retrieve all pipeline IDs under a given node.

        Args:
            node (TreeNode): The node to retrieve pipeline IDs from.

        Returns:
            set: A set of pipeline IDs.
        """
        pipeline_ids = set()
        if node.is_folder:
            for child in node.children:
                pipeline_ids.update(self.get_all_pipeline_ids(child))
        elif node.pipeline_id:
            pipeline_ids.add(node.pipeline_id)
        return pipeline_ids

    def are_all_pipelines_selected(self, node):
        """
        Check if all pipelines under the given node are selected.

        Args:
            node (TreeNode): The node to check.

        Returns:
            bool: True if all pipelines are selected, False otherwise.
        """
        pipeline_ids = self.get_all_pipeline_ids(node)
        return pipeline_ids.issubset(self.selected_pipelines)

    def select_pipelines(self, pipeline_ids):
        """
        Select multiple pipelines.

        Args:
            pipeline_ids (set): A set of pipeline IDs to select.
        """
        self.selected_pipelines.update(pipeline_ids)

    def deselect_pipelines(self, pipeline_ids):
        """
        Deselect multiple pipelines.

        Args:
            pipeline_ids (set): A set of pipeline IDs to deselect.
        """
        self.selected_pipelines.difference_update(pipeline_ids)

