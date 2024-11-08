# utils/tree.py

class TreeNode:
    def __init__(self, name, is_folder=False):
        self.name = name
        self.is_folder = is_folder
        self.children = []
        self.expanded = False  # Collapsed by default
        self.pipeline_id = None  # Only set for pipelines

    def add_child(self, child):
        self.children.append(child)

def build_tree(pipelines):
    root = TreeNode('root', is_folder=True)
    root.expanded = True  # Set root to expanded by default
    for pipeline in pipelines:
        folder_path = pipeline.get('folder', '\\')
        name = pipeline.get('name', 'Unnamed')
        nodes = folder_path.strip('\\').split('\\')
        current_node = root
        for node_name in nodes:
            if node_name:
                # Find existing child or create new
                found = next((child for child in current_node.children if child.name == node_name and child.is_folder), None)
                if not found:
                    found = TreeNode(node_name, is_folder=True)
                    current_node.add_child(found)
                current_node = found
        # Add pipeline as child
        pipeline_node = TreeNode(name)
        pipeline_node.pipeline_id = pipeline.get('id')
        current_node.add_child(pipeline_node)
    return root

# Optional utility function
def traverse_tree(node, action):
    action(node)
    if node.is_folder and node.expanded:
        for child in node.children:
            traverse_tree(child, action)

