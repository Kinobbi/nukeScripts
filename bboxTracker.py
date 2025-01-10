tracker = nuke.selectedNode()

bbox = tracker.bbox()
print(f"X: {bbox.x()} Y: {bbox.y()}")
print(f"R: {bbox.w() +  bbox.x()} T: {bbox.h() + bbox.y()}")

tracks = tracker['tracks']
columns = 31

point_index = 0
tracker = nuke.selectedNode()

frame = nuke.frame()

tracks.setValueAt(bbox.x(), frame, columns*0+2)
tracks.setValueAt(bbox.y(), frame, columns*0+3)

tracks.setValueAt(bbox.w() +  bbox.x(), frame, columns*1+2)
tracks.setValueAt(bbox.y(), frame, columns*1+3)

tracks.setValueAt(bbox.w() +  bbox.x(), frame, columns*2+2)
tracks.setValueAt(bbox.h() + bbox.y(), frame, columns*2+3)

tracks.setValueAt(bbox.x(), frame, columns*3+2)
tracks.setValueAt(bbox.h() + bbox.y(), frame, columns*3+3)

current_frame = nuke.frame()
nuke.frame(current_frame + 1)
