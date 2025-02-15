import nuke
import nukescripts

def refresh_blur_nodes(blur_group):
    """ Refresh the blur nodes inside the specific BlurChain group """
    blur_group.begin()  # Enter the correct group

    num_blurs = int(blur_group.knob("num_blurs").value())

    # Delete Existing Blur & Merge Nodes
    for node in nuke.allNodes():
        if node.Class() in ["Blur", "Merge2"]:
            nuke.delete(node)

    # Get the Group Input and Output Nodes
    input_node = nuke.toNode("Input1")
    output_node = nuke.toNode("Output1")

    if not input_node or not output_node:
        nuke.message(f"ERROR: Input1 or Output1 node not found in {blur_group.name()}!")
        blur_group.end()
        return

    blur_nodes = []  # Store all Blurs for merging

    for i in range(1, num_blurs + 1):
        blur_node = nuke.createNode("Blur", inpanel=False)  # Prevents properties panel from opening
        blur_node.setName(f"Blur{i}")

        # First Blur references the Group Size Control and Multiplier
        if i == 1:
            blur_node.knob("size").setExpression("parent.size_control")
        else:
            blur_node.knob("size").setExpression(f"parent.Blur{i-1}.size * parent.blur_multiplier")

        # Connect all Blur nodes to Input1
        blur_node.setInput(0, input_node)

        blur_nodes.append(blur_node)

    # Select all Blur nodes before creating the Merge node
    for blur in blur_nodes:
        blur["selected"].setValue(True)

    # Create the Merge2 node using nukescripts with inpanel=False
    merge_node = nukescripts.createNodeLocal("Merge2", "operation screen name Scrn", False)
    merge_node.knob("selected").setValue(False)  # Deselect after creation

    # Connect Merge node to Output1
    output_node.setInput(0, merge_node)

    blur_group.end()  # Exit the group

def create_blur_chain_group():
    # Create the Group Node
    blur_group = nuke.createNode("Group")
    blur_group.setName("BlurChain")

    # Enter the group context to create nodes inside it
    blur_group.begin()

    # Add Group Input and Output nodes
    input_node = nuke.createNode("Input", inpanel=False)
    input_node.setName("Input1")  # Ensures the correct input node

    output_node = nuke.createNode("Output", inpanel=False)
    output_node.setName("Output1")  # Ensures the correct output node

    # Create a Size Control Knob (for the first Blur node)
    size_knob = nuke.Double_Knob("size_control", "First Blur Size")
    size_knob.setValue(10)  # Default size
    blur_group.addKnob(size_knob)

    # Create a Multiplier Knob (replacing *2 in expressions)
    multiplier_knob = nuke.Double_Knob("blur_multiplier", "Blur Multiplier")
    multiplier_knob.setValue(2.0)  # Default multiplier (same as the original *2)
    multiplier_knob.setRange(0.1, 5.0)  # Allow flexible scaling
    blur_group.addKnob(multiplier_knob)

    # Create an Integer Knob to Control the Number of Blur Nodes (Set to Read-Only)
    num_blurs_knob = nuke.Int_Knob("num_blurs", "Number of Blurs")
    num_blurs_knob.setRange(1, 20)  # Allow up to 20 blurs
    num_blurs_knob.setValue(6)  # Default to 6
    num_blurs_knob.setFlag(nuke.DISABLED)  # Make it Read-Only
    blur_group.addKnob(num_blurs_knob)

    # Buttons for Increasing/Decreasing Blur Count
    add_button = nuke.PyScript_Knob("add_blur", "+", "n = nuke.thisNode(); n.knob('num_blurs').setValue(n.knob('num_blurs').value() + 1); refresh_blur_nodes(n)")
    remove_button = nuke.PyScript_Knob("remove_blur", "−", "n = nuke.thisNode(); n.knob('num_blurs').setValue(max(1, n.knob('num_blurs').value() - 1)); refresh_blur_nodes(n)")

    blur_group.addKnob(add_button)
    blur_group.addKnob(remove_button)

    # Exit the group context
    blur_group.end()

    # Run it once to initialize the first set of Blurs
    refresh_blur_nodes(blur_group)

    print(f"BlurChain group '{blur_group.name()}' created successfully!")

# Run the function to create the Blur Group
create_blur_chain_group()
