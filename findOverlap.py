import nuke

def find_overlapping_nodes():
    nodes = nuke.allNodes()
    overlapping_nodes = []

    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            if i >= j:
                continue

            # Get positions and dimensions
            x1, y1 = node1.xpos(), node1.ypos()
            x2, y2 = node2.xpos(), node2.ypos()

            width1, height1 = node1.screenWidth(), node1.screenHeight()
            width2, height2 = node2.screenWidth(), node2.screenHeight()

            # Check if nodes overlap
            if (
                x1 < x2 + width2 and
                x1 + width1 > x2 and
                y1 < y2 + height2 and
                y1 + height1 > y2
            ):
                overlapping_nodes.append((node1, node2))

    # Print results
    if overlapping_nodes:
        nuke.message("Found overlapping nodes!")
        for node1, node2 in overlapping_nodes:
            print(f"Overlap detected between {node1.name()} and {node2.name()}")
    else:
        nuke.message("No overlapping nodes found.")

# Run the function
find_overlapping_nodes()

nuke.toNode('Grade1').setSelected(True)
