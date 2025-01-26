import nuke
from PySide2 import QtWidgets, QtGui, QtCore

def create_color_ramp_widget():
    """Function to create the PySide2 widget with draggable sliders, Nuke's color picker, and add/remove buttons."""

    class ColorRampWidget(QtWidgets.QWidget):
        def __init__(self, knob):
            super(ColorRampWidget, self).__init__()
            self.knob = knob
            self.setMinimumSize(400, 150)

            # Default color stops (black and white)
            self.colors = [
                (0.0, QtGui.QColor(0, 0, 0)),   # Position 0 (black)
                (1.0, QtGui.QColor(255, 255, 255))  # Position 1 (white)
            ]
            self.selected_index = None  # Track selected slider

            # Layout setup
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

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)  # Enable anti-aliasing

            gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
            for position, color in self.colors:
                gradient.setColorAt(position, color)

            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(self.rect().adjusted(0, 0, 0, -50))  # Reserve space for buttons

            # Draw draggable slider handles
            for index, (position, color) in enumerate(self.colors):
                x_pos = int(position * self.width())

                # Compute inverted color for highlight
                inverted_color = QtGui.QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())

                # Highlight selected slider with inverted color
                if index == self.selected_index:
                    painter.setPen(QtGui.QPen(inverted_color, 3))
                else:
                    painter.setPen(QtGui.QPen(QtCore.Qt.white, 2))

                painter.setBrush(QtGui.QBrush(color))
                painter.drawEllipse(QtCore.QPoint(x_pos, self.height() // 3), 10, 10)

                # Inner black border for contrast
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
                painter.drawEllipse(QtCore.QPoint(x_pos, self.height() // 3), 10, 10)

        def add_color_slider(self):
            """Add a new slider at the midpoint and with an average color."""
            if len(self.colors) < 2:
                return  # Need at least two points to add new ones

            # Find the pair of sliders with the largest gap
            largest_gap_index = 0
            largest_gap = 0.0
            for i in range(len(self.colors) - 1):
                pos1, _ = self.colors[i]
                pos2, _ = self.colors[i + 1]
                gap = pos2 - pos1
                if gap > largest_gap:
                    largest_gap = gap
                    largest_gap_index = i

            # Compute midpoint position
            pos1, col1 = self.colors[largest_gap_index]
            pos2, col2 = self.colors[largest_gap_index + 1]
            new_pos = (pos1 + pos2) / 2

            # Compute average color
            avg_color = QtGui.QColor(
                (col1.red() + col2.red()) // 2,
                (col1.green() + col2.green()) // 2,
                (col1.blue() + col2.blue()) // 2
            )

            # Insert the new slider at the correct position
            self.colors.insert(largest_gap_index + 1, (new_pos, avg_color))
            self.update_knob_value()
            self.update()

        def remove_selected_slider(self):
            """Remove the selected slider if it's not the first or last one."""
            if self.selected_index is not None and len(self.colors) > 2:
                del self.colors[self.selected_index]
                self.selected_index = None  # Reset selection
                self.update_knob_value()
                self.update()

        def mousePressEvent(self, event):
            """Select a slider when clicked."""
            for i, (position, color) in enumerate(self.colors):
                x_pos = int(position * self.width())
                if abs(event.x() - x_pos) < 10:
                    self.selected_index = i
                    self.update()
                    break

        def mouseMoveEvent(self, event):
            if self.selected_index is not None:
                new_pos = max(0.0, min(1.0, event.x() / self.width()))
                self.colors[self.selected_index] = (new_pos, self.colors[self.selected_index][1])
                self.update()

        def mouseDoubleClickEvent(self, event):
            """Open Nuke's color picker with the current slider color."""
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
                        self.update_knob_value()
                    break

        def mouseReleaseEvent(self, event):
            self.update_knob_value()

        def update_knob_value(self):
            """Store the current ramp values into the Nuke knob."""
            ramp_values = [f"({pos:.2f}, {col.red()/255.0}, {col.green()/255.0}, {col.blue()/255.0})" 
                           for pos, col in self.colors]
            self.knob.setValue(' '.join(ramp_values))

        def set_ramp_values(self, value):
            """Load color positions from the knob string."""
            self.colors.clear()
            for part in value.split(") ("):
                elements = part.strip("()").split(", ")
                if len(elements) == 4:
                    pos = float(elements[0])
                    r, g, b = float(elements[1]) * 255, float(elements[2]) * 255, float(elements[3]) * 255
                    self.colors.append((pos, QtGui.QColor(int(r), int(g), int(b))))
            self.update()

    return ColorRampWidget

def color_ramp_knob():
    """Function that returns a PySide2 widget as a PyCustom_Knob for Nuke."""
    class ColorRampKnob(nuke.PyCustom_Knob):
        def __init__(self, name, label):
            super(ColorRampKnob, self).__init__(name, label)
            self.widget = None

        def makeUI(self):
            if not self.widget:
                self.widget = create_color_ramp_widget()(self)
            return self.widget

    return ColorRampKnob("color_ramp", "Color Ramp")

# Add color ramp knob to the selected node
selected_node = nuke.selectedNode()
if selected_node:
    knob_script = "color_ramp_knob()"
    if "color_ramp" not in selected_node.knobs():
        selected_node.addKnob(nuke.PyCustom_Knob("color_ramp", "Color Ramp", knob_script))
        nuke.message("Color Ramp with sliders added to the selected node.")
else:
    nuke.message("Please select a node first.")
