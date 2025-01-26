import nuke
from PySide2 import QtWidgets, QtGui, QtCore

def create_color_ramp_widget(storage_knob):
    class ColorRampWidget(QtWidgets.QWidget):
        def __init__(self, knob):
            super(ColorRampWidget, self).__init__()
            self.knob = knob
            self.storage_knob = storage_knob
            self.setMinimumSize(400, 150)

            # Load stored values or set defaults
            self.colors = self.load_stored_values()
            self.selected_index = None

            self.layout = QtWidgets.QVBoxLayout(self)
            self.ramp_area = QtWidgets.QWidget(self)
            self.layout.addWidget(self.ramp_area)

            # Add/remove buttons
            button_layout = QtWidgets.QHBoxLayout()
            self.add_button = QtWidgets.QPushButton("+")
            self.remove_button = QtWidgets.QPushButton("-")

            self.add_button.setFixedSize(30, 30)
            self.remove_button.setFixedSize(30, 30)

            self.add_button.clicked.connect(self.add_color_slider)
            self.remove_button.clicked.connect(self.remove_selected_slider)

            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.remove_button)
            button_layout.addStretch()
            self.layout.addLayout(button_layout)

        def load_stored_values(self):
            value = self.storage_knob.value()
            colors = []
            if value:
                for part in value.split(") ("):
                    elements = part.strip("()").split(", ")
                    if len(elements) == 4:
                        pos = float(elements[0])
                        r, g, b = float(elements[1]) * 255, float(elements[2]) * 255, float(elements[3]) * 255
                        colors.append((pos, QtGui.QColor(int(r), int(g), int(b))))
            else:
                colors = [
                    (0.0, QtGui.QColor(0, 0, 0)),
                    (1.0, QtGui.QColor(255, 255, 255))
                ]
            return colors

        def save_to_storage(self):
            ramp_values = [f"({pos:.2f}, {col.red()/255.0:.2f}, {col.green()/255.0:.2f}, {col.blue()/255.0:.2f})" 
                           for pos, col in self.colors]
            self.storage_knob.setValue(' '.join(ramp_values))

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
            for position, color in self.colors:
                gradient.setColorAt(position, color)

            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(self.rect().adjusted(0, 0, 0, -50))

            # Draw draggable sliders with selection highlight
            for index, (position, color) in enumerate(self.colors):
                x_pos = int(position * self.width())

                # Compute inverted color for selection highlight
                inverted_color = QtGui.QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())

                if index == self.selected_index:
                    painter.setPen(QtGui.QPen(inverted_color, 3))  # Highlight with inverted color
                else:
                    painter.setPen(QtGui.QPen(QtCore.Qt.white, 2))

                painter.setBrush(QtGui.QBrush(color))
                painter.drawEllipse(QtCore.QPoint(x_pos, self.height() // 3), 10, 10)

                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                painter.drawEllipse(QtCore.QPoint(x_pos, self.height() // 3), 10, 10)

        def add_color_slider(self):
            if len(self.colors) < 2:
                return

            largest_gap_index = max(range(len(self.colors) - 1), 
                                   key=lambda i: self.colors[i + 1][0] - self.colors[i][0])

            pos1, col1 = self.colors[largest_gap_index]
            pos2, col2 = self.colors[largest_gap_index + 1]
            new_pos = (pos1 + pos2) / 2

            avg_color = QtGui.QColor(
                (col1.red() + col2.red()) // 2,
                (col1.green() + col2.green()) // 2,
                (col1.blue() + col2.blue()) // 2
            )

            self.colors.insert(largest_gap_index + 1, (new_pos, avg_color))
            self.save_to_storage()
            self.update()

        def remove_selected_slider(self):
            if self.selected_index is not None and len(self.colors) > 2:
                del self.colors[self.selected_index]
                self.selected_index = None
                self.save_to_storage()
                self.update()

        def mousePressEvent(self, event):
            for i, (position, color) in enumerate(self.colors):
                x_pos = int(position * self.width())
                if abs(event.x() - x_pos) < 10:
                    self.selected_index = i
                    self.update()
                    break

        def mouseDoubleClickEvent(self, event):
            for i, (position, color) in enumerate(self.colors):
                x_pos = int(position * self.width())
                if abs(event.x() - x_pos) < 10:
                    current_color = (color.red() << 24) | (color.green() << 16) | (color.blue() << 8) | 255
                    nuke_color = nuke.getColor(current_color)

                    if nuke_color != 0:
                        r = (nuke_color >> 24) & 255
                        g = (nuke_color >> 16) & 255
                        b = (nuke_color >> 8) & 255
                        self.colors[i] = (position, QtGui.QColor(r, g, b))
                        self.save_to_storage()
                        self.update()
                    break

        def mouseMoveEvent(self, event):
            if self.selected_index is not None:
                new_pos = max(0.0, min(1.0, event.x() / self.width()))
                self.colors[self.selected_index] = (new_pos, self.colors[self.selected_index][1])
                self.save_to_storage()
                self.update()

        def mouseReleaseEvent(self, event):
            self.save_to_storage()
            self.update()

    return ColorRampWidget

def color_ramp_knob():
    class ColorRampKnob(nuke.PyCustom_Knob):
        def __init__(self, name, label, storage_knob):
            super(ColorRampKnob, self).__init__(name, label)
            self.widget = None
            self.storage_knob = storage_knob

        def makeUI(self):
            if not self.widget:
                self.widget = create_color_ramp_widget(self.storage_knob)(self)
            return self.widget

    return ColorRampKnob("color_ramp", "Color Ramp", storage_knob)

# Add color ramp knob with persistent storage to the selected node
selected_node = nuke.selectedNode()
if selected_node:
    if "storage_knob" not in selected_node.knobs():
        storage_knob = nuke.String_Knob("storage_knob", "Ramp Storage")
        selected_node.addKnob(storage_knob)
        storage_knob.setFlag(nuke.INVISIBLE)
    else:
        storage_knob = selected_node["storage_knob"]
        storage_knob.setFlag(nuke.INVISIBLE)

    knob_script = "color_ramp_knob()"
    if "color_ramp" not in selected_node.knobs():
        selected_node.addKnob(nuke.PyCustom_Knob("color_ramp", "Color Ramp", knob_script))
        nuke.message("Color Ramp with sliders added to the selected node.")
else:
    nuke.message("Please select a node first.")
