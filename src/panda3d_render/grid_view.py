from panda3d.core import LineSegs, NodePath, Vec3, TextNode
import logging

class GridView:
    """
    Renders a 3D environment including a wireframe cube and coordinate axes to simulate an immersive environment.
    """
    
    def __init__(self, parent: NodePath, grid_size: int = 100, spacing: float = 10.0, color=(1, 1, 1, 1)):
        self.parent = parent
        self.grid_size = grid_size
        self.spacing = spacing
        self.color = color
        self.node = NodePath("3D_Environment")
        self.node.reparent_to(self.parent)
        
        self._create_cube_grid()
        self._create_coordinate_axes()
        
        logging.info(f"3D Environment created with size {self.grid_size}, spacing {self.spacing}, and color {self.color}")
        logging.info("3D Environment and coordinate axes added to the scene")

    def _create_cube_grid(self):
        """
        Creates a wireframe cube to simulate a 3D environment reference.
        """
        cube_size = self.grid_size * self.spacing  # Define cube size based on grid_size and spacing

        # Define cube vertices
        vertices = [
            Vec3(-cube_size/2, -cube_size/2, -cube_size/2),
            Vec3(cube_size/2, -cube_size/2, -cube_size/2),
            Vec3(cube_size/2, cube_size/2, -cube_size/2),
            Vec3(-cube_size/2, cube_size/2, -cube_size/2),
            Vec3(-cube_size/2, -cube_size/2, cube_size/2),
            Vec3(cube_size/2, -cube_size/2, cube_size/2),
            Vec3(cube_size/2, cube_size/2, cube_size/2),
            Vec3(-cube_size/2, cube_size/2, cube_size/2)
        ]

        # Define cube edges (pairs of indices)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom edges
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top edges
            (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
        ]

        # Create LineSegs for cube edges
        lines = LineSegs()
        lines.set_color(*self.color)
        lines.set_thickness(1)

        for edge in edges:
            lines.move_to(vertices[edge[0]])
            lines.draw_to(vertices[edge[1]])

        cube_node = self.node.attach_new_node(lines.create())
        logging.info(f"Cube grid created with size {cube_size} units.")

    def _create_coordinate_axes(self):
        """
        Creates coordinate axes (X, Y, Z) to show orientation.
        """
        axis_length = self.grid_size * self.spacing / 4  # 1/4 of the cube size
        
        lines = LineSegs()
        lines.set_thickness(3)

        # X-axis (red)
        lines.set_color(1, 0, 0, 1)
        lines.move_to(0, 0, 0)
        lines.draw_to(axis_length, 0, 0)

        # Y-axis (green)
        lines.set_color(0, 1, 0, 1)
        lines.move_to(0, 0, 0)
        lines.draw_to(0, axis_length, 0)

        # Z-axis (blue)
        lines.set_color(0, 0, 1, 1)
        lines.move_to(0, 0, 0)
        lines.draw_to(0, 0, axis_length)

        axis_node = self.node.attach_new_node(lines.create())
        axis_node.set_light_off()

        # Add labels to the axes
        self._add_axis_label("X", Vec3(axis_length, 0, 0), (1, 0, 0, 1))
        self._add_axis_label("Y", Vec3(0, axis_length, 0), (0, 1, 0, 1))
        self._add_axis_label("Z", Vec3(0, 0, axis_length), (0, 0, 1, 1))

        logging.info("Coordinate axes created and added to the scene.")

    def _add_axis_label(self, text, position, color):
        """
        Adds a label to an axis.
        """
        label = TextNode(f'{text}_axis_label')
        label.set_text(text)
        label.set_text_color(*color)
        label_np = self.node.attach_new_node(label)
        label_np.set_pos(position)
        label_np.set_scale(5)  # Adjust scale as needed
        label_np.set_light_off()
        label_np.set_billboard_point_eye()