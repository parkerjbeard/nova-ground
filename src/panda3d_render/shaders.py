from panda3d.core import Shader

class ShaderProgram:
    """
    Manages the compilation and linking of vertex and fragment shaders.
    Provides methods to use the shader program in the rendering pipeline,
    including error checking for shader compilation and program linking.
    """

    def __init__(self, vertex_shader_file: str, fragment_shader_file: str):
        self.vertex_shader_file = vertex_shader_file
        self.fragment_shader_file = fragment_shader_file
        self.shader = self._load_shader()

    def _load_shader(self) -> Shader:
        """
        Loads and compiles the vertex and fragment shaders.
        Raises an exception if shader compilation or linking fails.
        """
        shader = Shader.make(Shader.SL_GLSL, 
            vertex=self.vertex_shader_file,
            fragment=self.fragment_shader_file
        )
        if not shader:
            raise RuntimeError(f"Failed to load shaders: {self.vertex_shader_file}, {self.fragment_shader_file}")
        return shader

    def get_shader(self) -> Shader:
        """
        Returns the compiled shader program.
        """
        return self.shader

    def apply(self, node):
        """
        Applies the shader to the given node.
        """
        node.set_shader(self.shader)