rotoNode = nuke.selectedNode()

rotoNode.setXpos( 0 - 6 )
rotoNode.setYpos( 0 - 6 )

print (rotoNode['xpos'].value())
print (rotoNode['ypos'].value())

for n in nuke.allNodes():
    nuke.autoplaceSnap( n )


for n in nuke.selectedNodes():
    nuke.autoplaceSnap( n )

import nuke




grid_x = nuke.toNode('preferences')['GridWidth'].value()
grid_y = nuke.toNode('preferences')['GridHeight'].value()
