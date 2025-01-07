import nuke

def move_parent_nodes_up(node, y_offset=int(nuke.toNode('preferences')['GridHeight'].value()), visited=None):
    """
    Recursively move all parent nodes of the given node up by y_offset units.
    Ensures that nodes are not moved more than once, even if they are part of multiple branches.
    """
    if visited is None:
        visited = set()

    if node is None or node in visited:
        return

    # Mark the node as visited before moving it
    visited.add(node)

    # Move the current node up by y_offset
    node.setYpos(node.ypos() - y_offset)

    # Recursively move the parent nodes
    for i in range(node.inputs()):
        parent_node = node.input(i)
        if parent_node:
            move_parent_nodes_up(parent_node, y_offset, visited)

# Get the currently selected node
try:
    selected_node = nuke.selectedNode()
    move_parent_nodes_up(selected_node)
except ValueError:
    nuke.message("No node is selected. Please select a node.")
