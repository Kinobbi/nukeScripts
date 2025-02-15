import nuke
import nukescripts

def refresh_erode_nodes(erode_group):
    """ Refresh the erode nodes inside the specific ErodeChain group """
    erode_group.begin()  # Enter the correct group

    num_erodes = int(erode_group.knob("num_erodes").value())
    multiplier = erode_group.knob("erode_multiplier").value()

    # Delete Existing Erode Nodes
    for node in nuke.allNodes():
        if node.Class() == "Erode":
            nuke.delete(node)

    # Get the Group Input and Output Nodes
    input_node = nuke.toNode("Input1")
    output_node = nuke.toNode("Output1")

    if not input_node or not output_node:
        nuke.message(f"ERROR: Input1 or Output1 node not found in {erode_group.name()}!")
        erode_group.end()
        return

    previous_node = input_node  # Start with Input1
    erode_nodes = []  # Store all Erode nodes

    for i in range(1, num_erodes + 1):
        erode_node = nuke.createNode("Erode", inpanel=False)  # Prevents properties panel from opening
        erode_node.setName(f"Erode{i}")

        # First Erode references the Group Size Control
        if i == 1:
            erode_node.knob("size").setExpression("parent.size_control")
        else:
            erode_node.knob("size").setExpression(f"parent.Erode{i-1}.size * parent.erode_multiplier")

        # Connect each Erode node to its predecessor
        erode_node.setInput(0, previous_node)
        previous_node = erode_node  # Update previous node reference

        erode_nodes.append(erode_node)

    # Connect the last Erode node directly to Output1
    if erode_nodes:
        output_node.setInput(0, erode_nodes[-1])

    erode_group.end()  # Exit the group

def create_erode_chain_group():
    # Create the Group Node
    erode_group = nuke.createNode("Group")
    erode_group.setName("ErodeChain")

    # Enter the group context to create nodes inside it
    erode_group.begin()

    # Add Group Input and Output nodes
    input_node = nuke.createNode("Input", inpanel=False)
    input_node.setName("Input1")  # Ensures the correct input node

    output_node = nuke.createNode("Output", inpanel=False)
    output_node.setName("Output1")  # Ensures the correct output node

    # Create a Size Control Knob (for the first Erode node)
    size_knob = nuke.Double_Knob("size_control", "First Erode Size")
    size_knob.setValue(10)  # Default size
    erode_group.addKnob(size_knob)

    # Create a Multiplier Knob to control step size
    multiplier_knob = nuke.Double_Knob("erode_multiplier", "Erode Multiplier")
    multiplier_knob.setValue(2.0)  # Default multiplier
    erode_group.addKnob(multiplier_knob)

    # Create an Integer Knob to Control the Number of Erode Nodes (Set to Read-Only)
    num_erodes_knob = nuke.Int_Knob("num_erodes", "Number of Erodes")
    num_erodes_knob.setRange(1, 20)  # Allow up to 20 Erodes
    num_erodes_knob.setValue(6)  # Default to 6
    num_erodes_knob.setFlag(nuke.DISABLED)  # Make it Read-Only
    erode_group.addKnob(num_erodes_knob)

    # Buttons for Increasing/Decreasing Erode Count
    add_button = nuke.PyScript_Knob("add_erode", "+", "n = nuke.thisNode(); n.knob('num_erodes').setValue(n.knob('num_erodes').value() + 1); refresh_erode_nodes(n)")
    remove_button = nuke.PyScript_Knob("remove_erode", "−", "n = nuke.thisNode(); n.knob('num_erodes').setValue(max(1, n.knob('num_erodes').value() - 1)); refresh_erode_nodes(n)")

    erode_group.addKnob(add_button)
    erode_group.addKnob(remove_button)

    # Exit the group context
    erode_group.end()

    # Run it once to initialize the first set of Erodes
    refresh_erode_nodes(erode_group)

    print(f"ErodeChain group '{erode_group.name()}' created successfully!")

# Run the function to create the Erode Chain Group
create_erode_chain_group()
